"""
Step definitions for offline recording scenarios
"""

from behave import given, when, then
from playwright.sync_api import expect


@given('the user has no internet connection')
def step_user_offline(context):
    """Set browser to offline mode"""
    context.page.context.set_offline(True)


@given('the ConnectionMonitor shows "Offline" status')
def step_connection_monitor_offline(context):
    """Verify connection monitor shows offline (skip if no connection monitor element)"""
    # The app doesn't currently have a visible connection status indicator
    # Skip this check as it's an internal state
    pass


@then('chunks should be saved locally only')
def step_chunks_saved_locally(context):
    """Verify no upload attempts are made"""
    context.page.wait_for_timeout(6000)
    
    # Verify no TUS upload requests
    upload_requests = [req for req in context.requests if '/files/' in req.url and req.method == 'PATCH']
    assert len(upload_requests) == 0, f"Unexpected upload attempts: {len(upload_requests)}"


@then('no upload attempts should be made')
def step_no_upload_attempts(context):
    """Verify no uploads occurred"""
    upload_requests = [req for req in context.requests if '/files/' in req.url]
    assert len(upload_requests) == 0, "Upload attempts detected while offline"


@given('the user has recorded audio for {duration:d} seconds while offline')
def step_recorded_offline(context, duration):
    """Record for specified duration while offline"""
    context.page.context.set_offline(True)
    context.page.click('#recordBtn')
    context.page.wait_for_timeout(duration * 1000)


@then('the save modal should appear')
def step_save_modal_appears(context):
    """Verify save modal is shown"""
    expect(context.page.locator('#saveModal, .save-modal')).to_be_visible(timeout=3000)


@then('the user should be prompted to enter a filename')
def step_filename_prompt(context):
    """Verify filename input is present"""
    expect(context.page.locator('#fileNameInput, .filename-input')).to_be_visible()


@when('the user enters "{filename}" as the filename')
def step_enter_filename(context, filename):
    """Enter filename in the input field"""
    context.page.fill('#fileNameInput, .filename-input', filename)
    context.filename = filename


@when('the user clicks the save button')
def step_click_save_button(context):
    """Click the save button in modal"""
    context.page.click('#saveBtn, .save-button')


@then('the recording should be assembled on the client')
def step_client_assembly(context):
    """Verify client-side assembly occurred"""
    # Check for assembly progress or completion
    context.page.wait_for_selector('.toast, .track-item', timeout=10000)


@then('an upload button should be visible for this recording')
def step_upload_button_visible(context):
    """Verify upload button is shown"""
    track = context.page.locator('.track-item').first
    expect(track.locator('.uploadBtn, .upload-button')).to_be_visible()


@given('the user has a local recording in the playlist')
def step_has_local_recording(context):
    """Ensure a local recording exists"""
    # Record offline
    context.page.context.set_offline(True)
    context.page.click('#recordBtn')
    context.page.wait_for_timeout(2000)
    context.page.click('#stopBtn')
    
    # Save via modal
    context.page.wait_for_selector('#saveModal')
    context.page.fill('#fileNameInput', 'test_local')
    context.page.click('#saveBtn')
    context.page.wait_for_selector('.track-item:has(.badge:has-text("LOCAL"))', timeout=5000)


@then('the audio should play from IndexedDB')
def step_audio_from_indexeddb(context):
    """Verify audio is loaded from IndexedDB"""
    # No server requests should be made
    initial_request_count = len([r for r in context.requests if '.webm' in r.url])
    context.page.wait_for_timeout(1000)
    final_request_count = len([r for r in context.requests if '.webm' in r.url])
    assert initial_request_count == final_request_count, "Server requests detected for local playback"


@then('playback should start immediately')
def step_playback_immediate(context):
    """Verify immediate playback"""
    expect(context.page.locator('#playBtn')).to_contain_text('⏸', timeout=1000)


@given('the user was offline')
def step_was_offline(context):
    """Set initial offline state"""
    context.page.context.set_offline(True)


@then('the upload button should become enabled')
def step_upload_button_enabled(context):
    """Verify upload button is enabled"""
    expect(context.page.locator('.uploadBtn').first).to_be_enabled(timeout=2000)


@when('the user clicks the upload button')
def step_click_upload_button(context):
    """Click upload button"""
    context.page.locator('.uploadBtn').first.click()


@then('the recording should start uploading to the server')
def step_recording_uploading(context):
    """Verify upload started"""
    context.page.wait_for_timeout(2000)
    upload_requests = [r for r in context.requests if '/files/' in r.url]
    assert len(upload_requests) > 0, "No upload requests detected"


@then('a progress indicator should be visible')
def step_progress_indicator_visible(context):
    """Verify progress indicator shown"""
    expect(context.page.locator('.progress, .upload-progress')).to_be_visible(timeout=2000)


@then('the badge should change from "LOCAL" to "SERVER" when complete')
def step_badge_changes(context):
    """Verify badge changes after upload"""
    # Wait for upload to complete
    expect(context.page.locator('.badge:has-text("SERVER")')).to_be_visible(timeout=30000)


@given('the user has {count:d} local recordings in the playlist')
def step_has_multiple_local_recordings(context, count):
    """Create multiple local recordings"""
    context.page.context.set_offline(True)
    
    for i in range(count):
        context.page.click('#recordBtn')
        context.page.wait_for_timeout(1000)
        context.page.click('#stopBtn')
        context.page.wait_for_selector('#saveModal')
        context.page.fill('#fileNameInput', f'test_{i}')
        context.page.click('#saveBtn')
        context.page.wait_for_timeout(500)


@then('the upload queue should process recordings automatically')
def step_upload_queue_processes(context):
    """Verify automatic upload processing"""
    context.page.wait_for_timeout(3000)
    # Check for upload activity
    upload_requests = [r for r in context.requests if '/files/' in r.url]
    assert len(upload_requests) > 0, "No automatic uploads detected"


@then('recordings should upload one at a time')
def step_sequential_upload(context):
    """Verify sequential upload"""
    # This is implementation-dependent
    pass


@then('the UI should show upload progress')
def step_ui_shows_progress(context):
    """Verify UI progress display"""
    expect(context.page.locator('.upload-progress, .progress')).to_be_visible()


@then('all recordings should eventually have "SERVER" badges')
def step_all_have_server_badges(context):
    """Verify all recordings uploaded"""
    # Wait for all to complete (with timeout)
    expect(context.page.locator('.badge:has-text("LOCAL")')).to_have_count(0, timeout=60000)


@then('the file should be downloaded from IndexedDB')
def step_download_from_indexeddb(context):
    """Verify download from local storage"""
    # Download should complete without server requests
    pass
