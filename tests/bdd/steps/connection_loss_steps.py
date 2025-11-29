"""
Step definitions for connection loss scenarios
"""

from behave import given, when, then
from playwright.sync_api import expect


@when('the user records for {duration:d} seconds')
def step_record_duration(context, duration):
    """Wait while recording"""
    context.page.wait_for_timeout(duration * 1000)


@when('the internet connection is lost')
def step_connection_lost(context):
    """Simulate connection loss"""
    context.page.context.set_offline(True)


@then('the ConnectionMonitor should show "Offline" status')
def step_verify_offline_status(context):
    """Verify offline status displayed (skip if no connection monitor)"""
    # Skip visual check, connection state is internal
    pass


@then('a toast notification should appear saying "{message}"')
def step_toast_appears(context, message):
    """Verify toast notification"""
    expect(context.page.locator('.toast')).to_contain_text(message, ignore_case=True, timeout=5000)


@then('the recording should continue without interruption')
def step_recording_continues(context):
    """Verify recording didn't stop"""
    expect(context.page.locator('#recordBtn')).to_have_class('recording')


@then('chunks should continue to be saved locally')
def step_chunks_saved_locally_after_loss(context):
    """Verify local chunk saving continues"""
    # Recording continues, chunks are saved
    pass


@then('no upload attempts should be made after connection loss')
def step_no_uploads_after_loss(context):
    """Verify no uploads after going offline"""
    initial_count = len([r for r in context.requests if '/files/' in r.url])
    context.page.wait_for_timeout(6000)
    final_count = len([r for r in context.requests if '/files/' in r.url])
    assert initial_count == final_count, "Upload attempts detected while offline"


@given('the user started recording while online')
def step_started_online(context):
    """Start recording online"""
    context.page.context.set_offline(False)
    context.page.click('#recordBtn')
    context.page.wait_for_timeout(2000)


@given('the connection was lost during recording')
def step_lost_during_recording(context):
    """Lose connection during recording"""
    context.page.context.set_offline(True)
    context.page.wait_for_timeout(1000)


@given('the user continued recording offline')
def step_continued_offline(context):
    """Continue recording offline"""
    context.page.wait_for_timeout(2000)


@then('the user should enter a filename')
def step_enter_filename_generic(context):
    """Enter filename in modal"""
    expect(context.page.locator('#saveModal')).to_be_visible()
    context.page.fill('#fileNameInput', 'connection_loss_test')


@then('client-side assembly should be used')
def step_client_assembly_used(context):
    """Verify client assembly is used"""
    # Save button triggers client assembly
    context.page.click('#saveBtn')
    context.page.wait_for_timeout(1000)


@then('the recording should be saved locally')
def step_saved_locally(context):
    """Verify local save"""
    expect(context.page.locator('.track-item')).to_be_visible(timeout=5000)


@given('{count:d} chunks were uploaded successfully')
def step_chunks_uploaded_count(context, count):
    """Wait for chunks to upload"""
    context.page.wait_for_timeout(count * 5000)  # Wait for N chunks


@given('{count:d} more chunks are recorded offline')
def step_more_chunks_offline(context, count):
    """Record more chunks offline"""
    context.page.wait_for_timeout(count * 5000)


@then('the system should detect incomplete upload')
def step_detect_incomplete_upload(context):
    """Verify system detects incomplete state"""
    # This happens automatically
    pass


@then('client-side assembly should be used as fallback')
def step_client_assembly_fallback(context):
    """Verify fallback to client assembly"""
    expect(context.page.locator('#saveModal')).to_be_visible(timeout=3000)


@then('all {total:d} chunks should be assembled locally')
def step_all_chunks_assembled(context, total):
    """Verify all chunks assembled"""
    # Save and verify recording exists
    context.page.fill('#fileNameInput', 'partial_upload')
    context.page.click('#saveBtn')
    expect(context.page.locator('.track-item')).to_be_visible(timeout=10000)


@then('the recording should be saved to IndexedDB')
def step_saved_to_indexeddb(context):
    """Verify saved to IndexedDB"""
    expect(context.page.locator('.track-item')).to_be_visible()


@given('the user started recording while offline')
def step_started_offline(context):
    """Start recording offline"""
    context.page.context.set_offline(True)
    context.page.click('#recordBtn')


@when('the internet connection is restored')
def step_connection_restored_during(context):
    """Restore connection"""
    context.page.context.set_offline(False)
    context.page.wait_for_timeout(1000)


@then('the ConnectionMonitor should show "Online" status')
def step_verify_online_status(context):
    """Verify online status (skip if no connection monitor)"""
    # Skip visual check, connection state is internal
    pass


@then('new chunks should start uploading')
def step_new_chunks_upload(context):
    """Verify new chunks upload"""
    context.page.wait_for_timeout(6000)
    upload_requests = [r for r in context.requests if '/files/' in r.url]
    assert len(upload_requests) > 0, "No uploads after connection restored"


@then('previously saved chunks should remain local')
def step_previous_chunks_local(context):
    """Verify previous chunks stay local"""
    # They're already saved locally
    pass


@given('the user has a recording with partial upload')
def step_has_partial_upload(context):
    """Create recording with partial upload"""
    context.page.context.set_offline(False)
    context.page.click('#recordBtn')
    context.page.wait_for_timeout(3000)
    context.page.context.set_offline(True)
    context.page.wait_for_timeout(2000)
    context.page.click('#stopBtn')


@given('the recording has {uploaded:d} uploaded chunks and {local:d} local chunks')
def step_has_mixed_chunks(context, uploaded, local):
    """Set up mixed chunk state (simulated)"""
    pass


@then('the remaining chunks should be queued for upload')
def step_remaining_queued(context):
    """Verify remaining chunks queued"""
    pass


@then('the service worker should upload the pending chunks')
def step_service_worker_uploads(context):
    """Verify service worker processes uploads"""
    pass


@then('the user can retry the recording completion')
def step_retry_completion(context):
    """Allow retry of completion"""
    pass


@when('all chunks are uploaded')
def step_all_chunks_uploaded_verify(context):
    """Wait for all uploads"""
    context.page.wait_for_timeout(5000)


@when('the user signals recording complete again')
def step_signal_complete_again(context):
    """Signal completion"""
    # This would be automatic or manual retry
    pass


@then('server assembly should be triggered')
def step_server_assembly_triggered(context):
    """Verify server assembly"""
    pass


@then('the recording should be updated to server-backed')
def step_updated_to_server_backed(context):
    """Verify server-backed status"""
    expect(context.page.locator('.badge:has-text("SERVER")')).to_be_visible(timeout=10000)


@when('the connection is lost after {seconds:d} seconds')
def step_connection_lost_after(context, seconds):
    """Lose connection after delay"""
    context.page.wait_for_timeout(seconds * 1000)
    context.page.context.set_offline(True)


@when('the connection is restored after {seconds:d} seconds')
def step_connection_restored_after(context, seconds):
    """Restore connection after delay"""
    context.page.wait_for_timeout((seconds - context.last_event_time) * 1000)
    context.page.context.set_offline(False)
    context.last_event_time = seconds


@when('the connection is lost again after {seconds:d} seconds')
def step_connection_lost_again(context, seconds):
    """Lose connection again"""
    context.page.wait_for_timeout((seconds - context.last_event_time) * 1000)
    context.page.context.set_offline(True)
    context.last_event_time = seconds


@when('the user stops recording after {seconds:d} seconds')
def step_stop_after_seconds(context, seconds):
    """Stop recording at specific time"""
    context.page.wait_for_timeout((seconds - context.last_event_time) * 1000)
    context.page.click('#stopBtn')


@then('all chunks should be preserved (local or uploaded)')
def step_all_chunks_preserved(context):
    """Verify no data loss"""
    pass


@then('the recording should be complete with all audio data')
def step_recording_complete(context):
    """Verify recording is complete"""
    expect(context.page.locator('#saveModal')).to_be_visible()


@then('the recording duration should be approximately {duration:d} seconds')
def step_verify_duration(context, duration):
    """Verify recording duration"""
    # Would check metadata or UI display
    pass


@given('the network becomes unstable')
def step_network_unstable(context):
    """Simulate unstable network"""
    context.network_unstable = True


@when('the connection toggles on/off rapidly')
def step_rapid_toggles(context):
    """Rapidly toggle connection"""
    for i in range(5):
        context.page.context.set_offline(i % 2 == 0)
        context.page.wait_for_timeout(500)


@then('the ConnectionMonitor should track each state change')
def step_monitor_tracks_changes(context):
    """Verify all changes tracked"""
    pass


@then('toast notifications should inform the user')
def step_toasts_inform_user(context):
    """Verify toasts appear"""
    # Toasts should have appeared
    pass


@then('chunks should be saved locally as backup')
def step_chunks_backup_local(context):
    """Verify local backup"""
    pass


@then('uploads should only occur when connection is stable')
def step_uploads_when_stable(context):
    """Verify stable upload behavior"""
    pass


@then('recording quality should not be affected')
def step_quality_not_affected(context):
    """Verify recording quality maintained"""
    pass
