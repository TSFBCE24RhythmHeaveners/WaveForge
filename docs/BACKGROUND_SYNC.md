# Background Sync Implementation

## Overview

This document describes the hybrid Background Sync implementation that allows uploads to continue even after the browser tab is closed or when network connectivity changes. The system coordinates between TUS.js uploads (for large files) and custom chunk uploads (during recording) while providing real-time visual status feedback.

## Architecture

### Components

1. **UploadCoordinator** (`frontend/src/index.html`)
   - Central registry for all active uploads
   - Tracks upload progress and status for each session
   - Handles connection state changes (online/offline)
   - Provides visual status feedback via badges
   - Coordinates between TUS and Custom upload methods

2. **Background Sync Event Handlers** (`frontend/src/sw.js`)
   - Listens for `sync` and `periodicsync` events
   - Processes upload queue when triggered
   - Sends progress messages to main thread
   - Handles errors and retries

3. **Status Badges** (CSS in `frontend/src/index.html`)
   - Visual indicators for upload states
   - Color-coded: Blue (uploading), Yellow (paused), Green (synced), Red (failed)
   - Animated pulse effect during active uploads

## Key Features

### 1. Background Sync API Integration

The system uses the Browser's Background Sync API to ensure uploads continue even after:
- Browser tab is closed
- Browser is minimized
- Device goes to sleep (limited support)

**Browser Support:**
- ✅ Chrome/Chromium (full support)
- ✅ Edge (full support)
- ✅ Opera (full support)
- ⚠️ Firefox (limited - requires flag)
- ❌ Safari (not supported)

**Fallback:** For unsupported browsers, uploads continue via Service Worker message passing.

### 2. Upload Coordination

**Registration:**
```javascript
// Register upload when recording starts
UploadCoordinator.registerUpload(sessionId, 'custom', totalChunks);
```

**Progress Tracking:**
```javascript
// Update progress as chunks upload
UploadCoordinator.updateProgress(sessionId, uploadedChunks, totalChunks);
```

**Completion:**
```javascript
// Mark upload as complete
UploadCoordinator.completeUpload(sessionId);
```

**Error Handling:**
```javascript
// Report errors
UploadCoordinator.failUpload(sessionId, errorMessage);
```

### 3. Connection Handling

**Online → Offline Transition:**
1. UploadCoordinator detects offline state
2. All active uploads marked as "paused"
3. Status badges change to yellow with "⏸ PAUSED"
4. Service Worker stops processing uploads
5. Connection check starts (every 5 seconds)

**Offline → Online Transition:**
1. UploadCoordinator detects online state
2. All paused uploads marked as "uploading"
3. Status badges change to blue with "⇪ X%"
4. Background Sync registered
5. Service Worker triggered to resume processing
6. Connection check stops

### 4. Visual Status Feedback

Each playlist item shows a status badge:

| Status | Badge | Color | Description |
|--------|-------|-------|-------------|
| Uploading | `⇪ 45%` | Blue | Upload in progress |
| Paused | `⏸ PAUSED` | Yellow | Upload paused (offline) |
| Synced | `✓ SYNCED` | Green | Upload complete |
| Failed | `❌ FAILED` | Red | Upload error (hover for details) |

### 5. Upload Methods

**Custom Upload (During Recording):**
- Used by Service Worker
- POST to `/upload/chunk`
- Sharded storage: `uploaded_data/{sessionId}/temp/shard_0000/{index}.part`
- Immediate chunk queueing as recorded

**TUS Upload (Main Thread):**
- Used for large files or recovery
- Resumable upload protocol
- Fallback for manual uploads
- Coordinated via UploadCoordinator

## Message Flow

### Service Worker → Main Thread

**Chunk Uploaded:**
```javascript
{
  type: 'CHUNK_UPLOADED',
  sessionId: 'sess_123...',
  chunkId: 5,
  totalChunks: 20
}
```

**Session Complete:**
```javascript
{
  type: 'SESSION_UPLOAD_COMPLETE',
  sessionId: 'sess_123...'
}
```

**Upload Error:**
```javascript
{
  type: 'UPLOAD_ERROR',
  sessionId: 'sess_123...',
  chunkId: 10,
  error: 'Server unreachable'
}
```

### Main Thread → Service Worker

**Force Unlock:**
```javascript
{
  type: 'PROCESS_UPLOADS',
  force: true
}
```

## Configuration

### Upload Timeout
```javascript
const UPLOAD_TIMEOUT = 60000; // 60 seconds max upload duration
```

### Retry Configuration
```javascript
const INITIAL_RETRY_DELAY = 2000; // 2 seconds
const MAX_RETRY_DELAY = 60000; // 60 seconds
const MAX_CONSECUTIVE_FAILURES = 10; // Max retries before max delay
```

### Connection Check Interval
```javascript
const CONNECTION_CHECK_INTERVAL = 5000; // Check every 5 seconds when offline
```

## Usage Examples

### Recording with Auto-Upload

1. **Start Recording:**
   ```javascript
   startRecording();
   // UploadCoordinator automatically registers upload
   ```

2. **During Recording:**
   - Chunks are saved to IndexedDB
   - Service Worker uploads in background
   - Progress badge shows "⇪ 35%"

3. **Connection Lost:**
   - Badge changes to "⏸ PAUSED"
   - Chunks queue in IndexedDB
   - Connection check starts

4. **Connection Restored:**
   - Badge returns to "⇪ 45%"
   - Uploads resume automatically

5. **Recording Complete:**
   - All chunks uploaded
   - Badge shows "✓ SYNCED" for 5 seconds
   - Badge disappears

### Manual Upload

1. **Click Cloud Button:**
   ```javascript
   UploadManager.queueUpload(id, blob, fileName, metadata, sessionId);
   ```

2. **Background Sync Registered:**
   - Upload continues even if tab closed
   - Re-opening tab shows current progress

3. **Upload Complete:**
   - Badge shows "✓ SYNCED"
   - File available in playlist

## Testing Scenarios

### Test 1: Online Recording
1. Start recording online
2. Verify badge shows "⇪ X%"
3. Stop recording
4. Verify badge shows "✓ SYNCED"

### Test 2: Offline Recording
1. Start recording online
2. Turn off network
3. Verify badge shows "⏸ PAUSED"
4. Continue recording (chunks queue)
5. Turn on network
6. Verify badge shows "⇪ X%" and uploads resume

### Test 3: Tab Close
1. Start recording
2. Close browser tab
3. Wait 30 seconds
4. Re-open tab
5. Verify upload continued in background

### Test 4: Upload Failure
1. Start recording
2. Stop server (simulate failure)
3. Verify badge shows "⏸ PAUSED"
4. Restart server
5. Verify uploads resume automatically

### Test 5: Multiple Sessions
1. Record multiple sessions
2. Verify each has independent status badge
3. Test connection changes affect all sessions
4. Verify coordination prevents conflicts

## Troubleshooting

### Issue: Badge Not Appearing
**Cause:** Session ID missing from recording
**Fix:** Ensure `currentSessionId` is set in `startRecording()`

### Issue: Upload Stuck
**Cause:** Upload lock timeout
**Fix:** Wait 60 seconds for auto-unlock, or send force unlock message

### Issue: Uploads Not Resuming
**Cause:** Background Sync not registered
**Fix:** Check browser compatibility, verify Service Worker is active

### Issue: Status Not Updating
**Cause:** Service Worker not sending messages
**Fix:** Check console for SW errors, verify `broadcastStatus()` calls

### Issue: Multiple Upload Methods Conflict
**Cause:** Both TUS and Custom upload running simultaneously
**Fix:** UploadCoordinator tracks method, prevents conflicts

## Performance Considerations

1. **Memory Usage:**
   - Chunks stored in IndexedDB (1MB each)
   - Blobs freed after successful upload
   - Total memory depends on queue size

2. **Network Usage:**
   - Uploads during recording (real-time)
   - Retries use exponential backoff
   - Maximum 10 retries before max delay

3. **CPU Usage:**
   - Service Worker processes uploads serially
   - Connection check every 5 seconds when offline
   - Upload coordinator updates UI on chunk completion

4. **Battery Impact:**
   - Background Sync minimizes battery usage
   - Periodic sync disabled by default (optional)
   - Connection checks stop when online

## Future Enhancements

1. **Periodic Background Sync:**
   - Enable for long-running uploads
   - Configurable interval
   - Requires additional permissions

2. **Upload Priority:**
   - Prioritize active recording sessions
   - Queue manual uploads
   - Dynamic bandwidth allocation

3. **Compression:**
   - Client-side chunk compression
   - Reduce network bandwidth
   - Faster upload times

4. **Analytics:**
   - Track upload success rate
   - Monitor retry patterns
   - Identify problematic sessions

5. **Advanced Retry Logic:**
   - Server-specific error handling
   - Smart retry scheduling
   - Adaptive timeout adjustment

## References

- [Background Sync API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Background_Synchronization_API)
- [Service Worker API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [TUS Protocol](https://tus.io/)
- [IndexedDB API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)

## Version History

- **v1.0.0** (2025-01-31): Initial hybrid Background Sync implementation
  - UploadCoordinator for central coordination
  - Background Sync event handlers
  - Visual status badges
  - Connection state handling
  - Integration with existing upload systems
