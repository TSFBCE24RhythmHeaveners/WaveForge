# WaveForge Pro - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Upload Lifecycle](#upload-lifecycle)
5. [Crash Recovery System](#crash-recovery-system)
6. [Chunk Integrity Guarantees](#chunk-integrity-guarantees)
7. [Retry & Backoff Strategy](#retry--backoff-strategy)
8. [Storage Architecture](#storage-architecture)
9. [API Design](#api-design)
10. [Performance Optimizations](#performance-optimizations)

---

## System Overview

WaveForge Pro is a web-based audio recording application with **guaranteed zero data loss** even during:
- Server crashes
- Network interruptions
- Browser/tab closes
- Page reloads

**Key Design Principles:**
1. **Durability First**: All data persisted before acknowledgment
2. **Fail-Safe**: Every operation has rollback/retry capability
3. **Observable**: Comprehensive logging at every step
4. **Idempotent**: Safe to retry any operation

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (Frontend)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             index.html (Main Thread)                 │  │
│  │  • MediaRecorder API                                 │  │
│  │  • UI Management                                     │  │
│  │  • UploadCoordinator                                │  │
│  │  • CrashGuard (Recovery System)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ postMessage()                   │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Service Worker (sw.js v2.3.3)                │  │
│  │  • Background Upload Processing                      │  │
│  │  • IndexedDB Queue Management                        │  │
│  │  • Retry Logic with Smart Backoff                   │  │
│  │  • Chunk Verification                                │  │
│  │  • Assembly Signal Coordination                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ HTTP/HTTPS                      │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Server (Python)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           backend/app/server.py                      │  │
│  │  • Chunk Upload Handler                              │  │
│  │  • Chunk Verification Endpoints                      │  │
│  │  • Sharded Storage Manager                           │  │
│  │  • File Assembly Logic                               │  │
│  │  • Atomic Write Operations                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Sharded File System                     │  │
│  │  uploaded_data/                                      │  │
│  │    └── {session_id}/                                 │  │
│  │        ├── temp/                                     │  │
│  │        │   ├── shard_0000/ (chunks 0-999)            │  │
│  │        │   ├── shard_0001/ (chunks 1000-1999)        │  │
│  │        │   └── ...                                   │  │
│  │        └── completed/                                │  │
│  │            ├── {filename}.webm                       │  │
│  │            └── {filename}.webm.meta.json             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Recording & Upload Flow

```
User Clicks "Start Recording"
    ↓
sessionId = generateSessionId()  // sess_{timestamp}_{random}
    ↓
MediaRecorder starts (1-second timeslices)
    ↓
Every 1 second:
    mediaRecorder.ondataavailable(blob)
        ↓
    Save to IndexedDB recovery_chunks
        ↓
    Queue in IndexedDB upload_queue
        ↓
    Service Worker triggered
        ↓
    Upload chunk to server (/upload/chunk)
        ↓
    Verify chunk on server (/api/verify/{session}/{chunk})
        ↓
    Remove from upload_queue (only if verified)
    ↓
User clicks "Stop" → "Save"
    ↓
Reset all retry delays (nextRetryAt = 0)
    ↓
Queue assembly signal
    ↓
Service Worker: All chunks uploaded?
    ↓
YES → Send /recording/complete
    ↓
Server assembles final file
    ↓
✅ Recording saved (zero missing chunks)
```

### Server Crash Recovery Flow

```
Recording in progress
    ↓
SERVER CRASHES (Ctrl+C)
    ↓
Chunks 10-15 fail upload
    ↓
Service Worker sets retry backoff:
  - Chunk 10: retryCount=1, nextRetryAt=now+1s
  - Chunk 11: retryCount=1, nextRetryAt=now+1s
    ↓
Recording continues (chunks 16-30 still queuing)
    ↓
SERVER RESTARTS
    ↓
Browser detects 'online' event
    ↓
ALL retry delays reset to 0
    ↓
Service Worker immediately processes queue
    ↓
Chunks 10-30 upload successfully
    ↓
User clicks SAVE → Assembly completes
    ↓
✅ Zero missing chunks
```

---

## Upload Lifecycle

### Chunk Processing States

```javascript
// IndexedDB: upload_queue
{
  id: "sess_123_chunk_42",
  sessionId: "sess_123",
  chunkIndex: 42,
  type: "chunk",
  blob: Blob,
  retryCount: 0,
  nextRetryAt: 0,        // 0 = retry immediately
  addedAt: 1733259102000
}

// State transitions:
QUEUED (nextRetryAt = 0)
    ↓
UPLOADING (fetch in progress)
    ↓
SUCCESS → VERIFYING
    ↓
VERIFIED → REMOVED FROM QUEUE
    
OR

FAILED → RETRY_BACKOFF (nextRetryAt = now + exponential delay)
    ↓
(wait for nextRetryAt)
    ↓
QUEUED (retry)
```

### Assembly Signal Coordination

```javascript
// Assembly signal is queued separately
{
  id: "sess_123_assembly",
  sessionId: "sess_123",
  type: "assembly_signal",
  fileName: "Recording.webm",
  metadata: {...},
  retryCount: 0,
  nextRetryAt: 0
}

// Service Worker checks:
if (type === 'assembly_signal') {
  remainingChunks = getChunksForSession(sessionId)
  
  if (remainingChunks.length > 0) {
    console.log('⏸ ASSEMBLY DELAYED - waiting for chunks')
    // Retry in 5 seconds
    nextRetryAt = now + 5000
    continue
  }
  
  // All chunks uploaded - send to server
  await fetch('/recording/complete', {...})
}
```

---

## Crash Recovery System

### Storage Structure

```javascript
// IndexedDB: WaveForgeDB_V4

Object Stores:
1. recovery_chunks
   - Key: "{sessionId}_chunk_{index}"
   - Purpose: Local backup for crash recovery
   - Cleared: When recording saved or discarded
   
2. upload_queue
   - Key: "{sessionId}_chunk_{index}" or "{sessionId}_assembly"
   - Purpose: Active upload queue
   - Cleared: When items successfully uploaded and verified
   
3. upload_sessions
   - Key: sessionId
   - Purpose: Track TUS upload sessions
```

### Recovery Flow

```javascript
// On page load
window.addEventListener('load', async () => {
  const sessions = await CrashGuard.getRecoverableSessions()
  
  if (sessions.length > 0) {
    showRecoveryModal(sessions)
  }
})

// User clicks "RECOVER"
async function recoverSession(sessionId) {
  const chunks = await CrashGuard.getRecoveryChunks(sessionId)
  
  // Re-queue all chunks
  for (const chunk of chunks) {
    await uploadChunkLive(sessionId, chunk.blob, chunk.chunkIndex)
  }
  
  // Queue assembly signal
  await queueRecordingComplete(sessionId, fileName, metadata)
  
  // Clear recovery data
  await CrashGuard.clearRecoveryChunks(sessionId)
  
  // Trigger Service Worker
  postMessage({ type: 'TRIGGER_UPLOAD' })
}
```

---

## Chunk Integrity Guarantees

### Client-Side Protection

**1. Double Queue System:**
```javascript
// recovery_chunks: Survives browser crash
await db.transaction('recovery_chunks', 'readwrite')
  .objectStore('recovery_chunks')
  .add({
    id: `${sessionId}_chunk_${index}`,
    blob: chunk,
    timestamp: Date.now()
  })

// upload_queue: Active uploads
await db.transaction('upload_queue', 'readwrite')
  .objectStore('upload_queue')
  .add({
    id: `${sessionId}_chunk_${index}`,
    blob: chunk,
    retryCount: 0,
    nextRetryAt: 0
  })
```

**2. Verification Before Removal:**
```javascript
// Upload
const uploadResult = await uploadChunk(...)

// Verify
const verifyResult = await fetch(`/api/verify/${session}/${chunk}`)
if (!verifyResult.exists) {
  throw new Error('Verification failed')
}

// Only NOW remove from queue
await removeFromQueue(db, itemId)
```

**3. Never Delete on Retry Exhaustion:**
```javascript
if (retryCount >= 20) {
  // Set long backoff, but KEEP in queue
  nextRetryAt = now + 300000  // 5 minutes
  // Chunk is NEVER deleted!
}
```

### Server-Side Protection

**1. Atomic Write Pattern:**
```python
# Write to temp file
chunk_tmp = chunk_path.with_suffix('.tmp')
with open(chunk_tmp, 'wb') as f:
    f.write(data)
    f.flush()
    os.fsync(f.fileno())  # Force write to disk

# Atomic rename
chunk_tmp.rename(chunk_path)

# Sync parent directory (persists directory entry)
parent_fd = os.open(chunk_path.parent, os.O_RDONLY)
os.fsync(parent_fd)
os.close(parent_fd)
```

**2. Size Validation on "Already Exists":**
```python
if chunk_path.exists():
    existing_size = chunk_path.stat().st_size
    incoming_size = len(await file.read())
    
    if existing_size != incoming_size:
        # Corrupted! Delete and re-upload
        chunk_path.unlink()
```

**3. Deep Verification:**
```python
# Not just file.exists(), but READ data
with open(chunk_path, 'rb') as f:
    first_byte = f.read(1)  # Forces disk access
    if not first_byte:
        return {"exists": False, "reason": "unreadable"}
```

**4. Orphaned File Cleanup:**
```python
# On server startup
for tmp_file in UPLOAD_DIR.rglob("*.tmp"):
    tmp_file.unlink()  # Remove incomplete uploads
```

---

## Retry & Backoff Strategy

### Exponential Backoff

```javascript
const retryDelay = Math.min(
  1000 * Math.pow(2, retryCount),  // Exponential
  300000                            // Max 5 minutes
)

// Timeline:
// Retry 1:  1 second
// Retry 2:  2 seconds
// Retry 3:  4 seconds
// Retry 4:  8 seconds
// Retry 5:  16 seconds
// Retry 6:  32 seconds
// Retry 7:  64 seconds
// Retry 8:  128 seconds (2:08)
// Retry 9:  256 seconds (4:16)
// Retry 10+: 300 seconds (5:00) - capped
```

### Smart Reset on Events

**On SAVE:**
```javascript
// In saveTrackToDB()
const items = await getItemsForSession(sessionId)

for (const item of items) {
  if (item.nextRetryAt > Date.now()) {
    item.nextRetryAt = 0              // Immediate retry
    item.retryCount = Math.max(0, item.retryCount - 1)
    await updateItem(item)
  }
}

postMessage({ type: 'TRIGGER_UPLOAD' })
```

**On Connection Restore:**
```javascript
window.addEventListener('online', async () => {
  const allItems = await getAllQueuedItems()
  
  for (const item of allItems) {
    if (item.nextRetryAt > Date.now()) {
      item.nextRetryAt = 0
      item.retryCount = Math.max(0, item.retryCount - 1)
      await updateItem(item)
    }
  }
  
  postMessage({ type: 'TRIGGER_UPLOAD' })
})
```

**Why This Works:**
- Problem: After server restart, chunks wait 32s, 64s, or 5 minutes
- Solution: Reset delays when connection restored or user saves
- Result: Uploads complete in seconds instead of minutes

---

## Storage Architecture

### Sharded Directory Structure

```
uploaded_data/
└── sess_1764712394002_m2x9p03vf/
    ├── temp/
    │   ├── shard_0000/          (chunks 0-999)
    │   │   ├── 0.part
    │   │   ├── 1.part
    │   │   └── 999.part
    │   ├── shard_0001/          (chunks 1000-1999)
    │   │   ├── 1000.part
    │   │   ├── 1001.part
    │   │   └── 1999.part
    │   └── shard_0002/          (chunks 2000-2999)
    │       └── ...
    └── completed/
        ├── Recording 22:54:02.webm
        └── Recording 22:54:02.webm.meta.json
```

### Shard Calculation

```python
CHUNKS_PER_SHARD = 1000

def get_chunk_path(session_id: str, chunk_index: int) -> Path:
    shard_number = chunk_index // CHUNKS_PER_SHARD
    shard_dir = f"shard_{shard_number:04d}"
    
    return (
        UPLOAD_DIR / session_id / "temp" / shard_dir / f"{chunk_index}.part"
    )

# Examples:
# Chunk 0    → temp/shard_0000/0.part
# Chunk 999  → temp/shard_0000/999.part
# Chunk 1000 → temp/shard_0001/1000.part
# Chunk 5432 → temp/shard_0005/5432.part
```

**Why Sharding?**
- File systems slow down with >10,000 files per directory
- Sharding provides O(1) lookup vs O(n) without
- Better performance, easier management

---

## API Design

### REST Endpoints

#### 1. Upload Chunk
```
POST /upload/chunk

Form Data:
  session_id: string      (e.g., "sess_1764712394002_m2x9p03vf")
  chunk_index: int        (e.g., 42)
  file: binary            (audio chunk blob)

Response 200 OK:
{
  "status": "chunk_received" | "chunk_already_exists",
  "chunk_index": 42,
  "session_id": "sess_..."
}

Idempotent: YES (safe to retry)
Timeout: 30 seconds (client-side)
```

#### 2. Verify Chunk
```
GET /api/verify/{session_id}/{chunk_index}

Response 200 OK:
{
  "exists": true,
  "size": 48000,
  "chunk_index": 42,
  "session_id": "sess_..."
}

Response 200 (Not Found):
{
  "exists": false,
  "chunk_index": 42
}

Idempotent: YES (read-only)
Timeout: 10 seconds (client-side)
```

#### 3. Complete Recording
```
POST /recording/complete

Form Data:
  session_id: string
  file_name: string
  metadata: string (JSON)

Response 200 OK:
{
  "status": "completed",
  "session_id": "sess_...",
  "file_name": "Recording.webm",
  "total_chunks": 155,
  "total_size": 3145728,
  "missing_chunks": []  // Should always be empty!
}

Idempotent: NO (creates final file)
Timeout: None (server waits for assembly)
```

---

## Performance Optimizations

### 1. Serial Upload Processing
```javascript
// Service Worker processes queue serially
for (const item of queue) {
  await uploadChunk(item)  // Sequential
}

// Why? Prevents:
// - Out-of-order assembly
// - Concurrent verification conflicts
// - IndexedDB transaction collisions
```

### 2. Batch Status Updates
```javascript
// Max 10 updates/second
let updateTimer = null

function scheduleStatusUpdate() {
  if (updateTimer) return
  
  updateTimer = setTimeout(() => {
    broadcastStatus(...)
    updateTimer = null
  }, 100)
}
```

### 3. IndexedDB Transaction Optimization
```javascript
// Good: Single transaction
const tx = db.transaction('upload_queue', 'readwrite')
const store = tx.objectStore('upload_queue')
for (const chunk of chunks) {
  await store.add(chunk)
}
await tx.complete
```

### 4. Blob Memory Management
```javascript
// Blobs automatically GC'd after removal from queue
async function uploadChunk(item) {
  await fetch('/upload/chunk', { body: item.blob })
  await verifyChunk(...)
  await removeFromQueue(...)  // Blob freed here
}
```

---

## Error Handling

### Client-Side

**Upload Timeout:**
```javascript
fetch(url, { signal: AbortSignal.timeout(30000) })
  .catch(error => {
    if (error.name === 'TimeoutError') {
      // Retry with backoff
    }
  })
```

**Verification Failure:**
```javascript
const result = await verifyChunk(sessionId, chunkIndex)
if (!result.exists) {
  throw new Error('Chunk not found on server')
  // Stays in queue, will retry
}
```

### Server-Side

**Disk Full:**
```python
try:
    with open(chunk_path_tmp, 'wb') as f:
        f.write(data)
except OSError as e:
    if e.errno == 28:  # ENOSPC
        raise HTTPException(503, "Disk full")
```

**Corrupted Chunks:**
```python
if existing_size != incoming_size:
    chunk_path.unlink()  # Delete corrupted
    # Fall through to re-upload
```

---

## Security Considerations

### Current Implementation (Development)
- ✅ CORS enabled for configured origins
- ✅ Security headers middleware
- ✅ Trusted host middleware
- ✅ Input validation (session_id, file_name)
- ⚠️ Basic authentication (SECRET_KEY in env)
- ⚠️ No rate limiting yet
- ⚠️ No file size limits per session

### Production Recommendations

**1. Authentication:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/upload/chunk")
async def upload_chunk(
    ...,
    token: str = Depends(security)
):
    if not verify_token(token):
        raise HTTPException(401, "Unauthorized")
```

**2. Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/upload/chunk")
@limiter.limit("100/minute")
async def upload_chunk(...):
    ...
```

**3. File Validation:**
```python
MAX_CHUNK_SIZE = 1_000_000  # 1 MB
ALLOWED_MIME_TYPES = ['audio/webm', 'audio/ogg']

if len(chunk_data) > MAX_CHUNK_SIZE:
    raise HTTPException(413, "Chunk too large")

if file.content_type not in ALLOWED_MIME_TYPES:
    raise HTTPException(415, "Invalid MIME type")
```

---

## Monitoring & Debugging

### Client-Side Logging

```javascript
// Enable verbose logging
localStorage.setItem('SW_DEBUG', 'true')

// Console output:
🎤 Recording chunk 42 (48000 bytes)
💾 Chunk 42 saved to IndexedDB
[SW] Uploading chunk 42
[SW] ✅ Chunk 42 verified (48000 bytes, readable)
📤 Chunk 43/155 uploaded
```

### Server-Side Logging

```python
# Console output:
✓ Chunk 42 received and saved
🔍 Verify request: session=sess_..., chunk=42
✓ Chunk 42 verified (48000 bytes, readable)
```

### Queue Inspection

```javascript
// In browser console
async function inspectQueue() {
  const db = await indexedDB.open('WaveForgeDB_V4', 3)
  const tx = db.transaction('upload_queue', 'readonly')
  const items = await tx.objectStore('upload_queue').getAll()
  
  console.table(items.map(item => ({
    sessionId: item.sessionId,
    chunkIndex: item.chunkIndex,
    retryCount: item.retryCount,
    nextRetry: new Date(item.nextRetryAt).toLocaleTimeString(),
    size: item.blob?.size
  })))
}

await inspectQueue()
```

---

## Version History

### v2.3.3 (2025-12-03)
- **Critical Fix:** Chunks no longer deleted from queue on SAVE
- **Critical Fix:** Retry delays reset immediately on SAVE
- **Critical Fix:** Retry delays reset on connection restore
- **Fixed:** Service Worker syntax error (duplicate processUploads)
- **Added:** Chunk size validation on server
- **Added:** Orphaned .tmp file cleanup
- **Improved:** Assembly signal sorting (process LAST)

### v2.2.0 (2025-12-03)
- **Added:** Sharded chunk storage
- **Added:** Chunk verification endpoints
- **Added:** Live upload progress indicator
- **Fixed:** Upload box visibility issues

### v2.1.0 (2025-12-02)
- **Added:** Service Worker background processing
- **Added:** IndexedDB persistent queue
- **Added:** Crash recovery system

---

## Glossary

- **Chunk**: 1-second audio segment (typically 40-50 KB)
- **Session**: Single recording instance with unique ID
- **Shard**: Subdirectory containing up to 1000 chunks
- **Queue**: IndexedDB object store for pending uploads
- **Verification**: Confirming chunk exists on server before queue removal
- **Assembly**: Combining all chunks into final file
- **Backoff**: Exponential delay between retry attempts
- **Idempotent**: Operation safe to retry without side effects

---

**Document Version:** 2.3.3  
**Last Updated:** 2025-12-03  
**Author:** WaveForge Pro Development Team
