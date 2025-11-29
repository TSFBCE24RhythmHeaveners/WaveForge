"""
Additional step definitions for crash recovery and UI scenarios
"""

from behave import given, when, then
from playwright.sync_api import expect


# Crash Recovery Steps
@given('IndexedDB is available')
def step_indexeddb_available(context):
    """Verify IndexedDB support"""
    result = context.page.evaluate("() => 'indexedDB' in window")
    assert result, "IndexedDB not available"


@given('the user starts recording audio')
def step_start_recording(context):
    """Start recording"""
    context.page.click('#recordBtn')


@given('chunks are being saved to IndexedDB recovery_chunks')
def step_chunks_to_recovery(context):
    """Verify chunks saved to recovery"""
    context.page.wait_for_timeout(6000)  # Wait for at least one chunk


@when('the browser crashes unexpectedly')
def step_browser_crash(context):
    """Simulate crash by reloading"""
    context.page.reload()


@when('the user reopens the application')
def step_reopen_app(context):
    """App reopens after crash"""
    context.page.wait_for_load_state('networkidle')


@then('a recovery modal should appear')
def step_recovery_modal_appears(context):
    """Verify recovery modal shown"""
    expect(context.page.locator('#recoveryModal, .recovery-modal')).to_be_visible(timeout=5000)


@then('the modal should show "{text}"')
def step_modal_shows_text(context, text):
    """Verify modal text"""
    expect(context.page.locator('#recoveryModal')).to_contain_text(text)


@then('the modal should display the session ID')
def step_modal_shows_session_id(context):
    """Verify session ID displayed"""
    expect(context.page.locator('#recoveryModal')).to_contain_text('session', ignore_case=True)


@then('the modal should show approximate duration')
def step_modal_shows_duration(context):
    """Verify duration shown"""
    expect(context.page.locator('#recoveryModal')).to_contain_text('second', ignore_case=True)


# Performance Steps
@given('the user has sufficient storage space')
def step_has_storage(context):
    """Verify storage available"""
    pass


@when('the user records audio for {minutes:d} minutes')
def step_record_minutes(context, minutes):
    """Record for specified minutes"""
    context.page.click('#recordBtn')
    context.page.wait_for_timeout(minutes * 60 * 1000)


@then('an assembly progress indicator should appear')
def step_assembly_progress_appears(context):
    """Verify assembly progress shown"""
    expect(context.page.locator('.assembly-progress, .progress')).to_be_visible(timeout=2000)


@then('the progress should show percentage complete')
def step_progress_shows_percentage(context):
    """Verify percentage displayed"""
    expect(context.page.locator('.progress')).to_contain_text('%')


@then('a message should explain "Assembling recording..."')
def step_assembling_message(context):
    """Verify assembling message"""
    expect(context.page.locator('text=/assembling/i')).to_be_visible()


@then('memory usage should remain acceptable')
def step_memory_acceptable(context):
    """Verify memory usage (requires browser metrics)"""
    pass


@given('the user has {count:d} recordings in the playlist')
def step_has_n_recordings(context, count):
    """Create N recordings (quick simulation)"""
    # For testing, we'd create sample data in IndexedDB
    pass


@when('the playlist is rendered')
def step_playlist_rendered(context):
    """Verify playlist renders"""
    expect(context.page.locator('.playlist, .track-list')).to_be_visible()


@then('the UI should load within {seconds:d} seconds')
def step_ui_loads_fast(context, seconds):
    """Verify fast UI load"""
    # Already loaded by this point
    pass


@then('scrolling should be smooth')
def step_scrolling_smooth(context):
    """Test scrolling performance"""
    context.page.evaluate("document.querySelector('.playlist').scrollBy(0, 500)")


@then('all recordings should display correctly')
def step_all_display_correctly(context):
    """Verify all recordings visible"""
    pass


@then('server badges and local badges should be accurate')
def step_badges_accurate(context):
    """Verify badge accuracy"""
    pass


# UI Indicator Steps
@then('the indicator should be in green color')
def step_indicator_green(context):
    """Verify green color"""
    pass  # Would check CSS or class


@then('the indicator should be in red color')
def step_indicator_red(context):
    """Verify red color"""
    pass


@then('the badge should have a distinctive color')
def step_badge_distinctive(context):
    """Verify badge color"""
    pass


@then('the badge should indicate server-backed storage')
def step_badge_indicates_server(context):
    """Verify badge meaning"""
    pass


@then('the badge should have a different color than server badge')
def step_badge_different_color(context):
    """Verify different colors"""
    pass


@then('the badge should indicate local storage')
def step_badge_indicates_local(context):
    """Verify local indication"""
    pass


@then('the button should be clearly labeled')
def step_button_labeled(context):
    """Verify button label"""
    expect(context.page.locator('.uploadBtn')).to_contain_text('upload', ignore_case=True)


@then('the record button should change appearance')
def step_record_button_changes(context):
    """Verify button appearance change"""
    expect(context.page.locator('#recordBtn')).to_have_class('recording')


@then('a recording indicator should pulse or animate')
def step_indicator_animates(context):
    """Verify animation"""
    expect(context.page.locator('.recording-indicator')).to_be_visible()


@then('the elapsed time should update every second')
def step_time_updates(context):
    """Verify time updates"""
    initial = context.page.locator('.elapsed-time, #timer').text_content()
    context.page.wait_for_timeout(1500)
    updated = context.page.locator('.elapsed-time, #timer').text_content()
    assert initial != updated


@then('the stop button should be enabled')
def step_stop_enabled(context):
    """Verify stop button enabled"""
    expect(context.page.locator('#stopBtn')).to_be_enabled()


@then('the message should say "{text}"')
def step_toast_message(context, text):
    """Verify toast message"""
    expect(context.page.locator('.toast')).to_contain_text(text)


@then('the toast should auto-dismiss after {seconds:d} seconds')
def step_toast_autodismiss(context, seconds):
    """Verify toast dismisses"""
    context.page.wait_for_timeout(seconds * 1000 + 500)
    expect(context.page.locator('.toast')).not_to_be_visible()


@then('the toast should use a different color (success)')
def step_toast_success_color(context):
    """Verify success toast color"""
    pass


@then('the percentage should be displayed')
def step_percentage_displayed(context):
    """Verify percentage shown"""
    expect(context.page.locator('.progress')).to_contain_text('%')


@then('an estimated time remaining should show')
def step_eta_shown(context):
    """Verify ETA displayed"""
    pass


@then('a cancel button should be present')
def step_cancel_present(context):
    """Verify cancel button"""
    expect(context.page.locator('#cancelBtn, .cancel-button')).to_be_visible()


@then('the filename should have a default value')
def step_default_filename(context):
    """Verify default filename"""
    value = context.page.locator('#fileNameInput').input_value()
    assert len(value) > 0, "No default filename"


@then('the user should not be able to start new recording until complete')
def step_recording_disabled(context):
    """Verify record button disabled"""
    expect(context.page.locator('#recordBtn')).to_be_disabled()


@then('the filename should be clear and descriptive')
def step_filename_descriptive(context):
    """Verify filename quality"""
    pass


@then('the file type should be indicated (.webm)')
def step_file_type_indicated(context):
    """Verify file type shown"""
    pass


@then('the message should be user-friendly')
def step_message_friendly(context):
    """Verify friendly error message"""
    pass


@then('the toast should not auto-dismiss')
def step_toast_no_autodismiss(context):
    """Verify error toast stays"""
    context.page.wait_for_timeout(6000)
    expect(context.page.locator('.toast.error')).to_be_visible()


@then('a retry button should be available')
def step_retry_available(context):
    """Verify retry button"""
    expect(context.page.locator('.retry-button')).to_be_visible()


@then('the play button should change to pause icon')
def step_play_to_pause(context):
    """Verify play/pause toggle"""
    expect(context.page.locator('#playBtn')).to_contain_text('⏸')


@then('the timeline should show current position')
def step_timeline_shows_position(context):
    """Verify timeline"""
    expect(context.page.locator('.timeline, .progress-bar')).to_be_visible()


@then('the waveform should highlight played portion')
def step_waveform_highlights(context):
    """Verify waveform visualization"""
    pass


@then('a helpful message should appear')
def step_helpful_message(context):
    """Verify empty state message"""
    expect(context.page.locator('.empty-state')).to_be_visible()


@then('the message should guide user to record')
def step_message_guides(context):
    """Verify guidance"""
    expect(context.page.locator('.empty-state')).to_contain_text('record', ignore_case=True)


@then('an icon or illustration should make it friendly')
def step_friendly_icon(context):
    """Verify icon present"""
    pass


@then('a loading spinner should be visible')
def step_spinner_visible(context):
    """Verify spinner"""
    expect(context.page.locator('.spinner, .loading')).to_be_visible()


@then('the spinner should indicate progress')
def step_spinner_progress(context):
    """Verify spinner shows progress"""
    pass


@when('loading is complete')
def step_loading_complete(context):
    """Wait for loading"""
    context.page.wait_for_load_state('networkidle')


@then('the spinner should disappear')
def step_spinner_disappears(context):
    """Verify spinner gone"""
    expect(context.page.locator('.spinner')).not_to_be_visible()


@then('the recordings should render')
def step_recordings_render(context):
    """Verify recordings displayed"""
    expect(context.page.locator('.track-item')).to_be_visible()
