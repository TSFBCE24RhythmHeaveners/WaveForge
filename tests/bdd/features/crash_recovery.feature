Feature: Crash Recovery and Data Persistence
  As a user whose browser or app crashes
  I want to recover my recording after restart
  So that I don't lose valuable audio data

  Background:
    Given the WaveForge Pro application is loaded
    And IndexedDB is available

  Scenario: Recovery after browser crash during recording
    Given the user starts recording audio
    And the user records for 10 seconds
    And chunks are being saved to IndexedDB recovery_chunks
    When the browser crashes unexpectedly
    And the user reopens the application
    Then a recovery modal should appear
    And the modal should show "1 recording can be recovered"
    And the modal should display the session ID
    And the modal should show approximate duration

  Scenario: Successful recovery and upload
    Given the user has a crashed recording session
    And the recovery modal is displayed
    When the user clicks the "Recover" button
    Then the application should read chunks from recovery_chunks
    And the chunks should be uploaded to the server
    And a progress indicator should show upload status
    When all chunks are uploaded
    Then server assembly should be triggered
    And the recording should appear in the playlist
    And the recording should have a "SERVER" badge
    And the recovery_chunks for this session should be cleaned up

  Scenario: Recovery to local storage when offline
    Given the user has a crashed recording session
    And the user is currently offline
    When the user clicks the "Recover" button
    Then the chunks should be assembled locally
    And the save modal should appear
    When the user enters "recovered_offline" as filename
    And clicks save
    Then the recording should be saved to IndexedDB
    And the recording should appear in the playlist with "LOCAL" badge
    And the recording should be queued for upload when online

  Scenario: Discard recovered recording
    Given the user has a crashed recording session
    And the recovery modal is displayed
    When the user clicks the "Discard" button
    Then the recovery_chunks for this session should be deleted
    And the recovery modal should close
    And no recording should be added to the playlist

  Scenario: Multiple crashed sessions recovery
    Given the user has 3 crashed recording sessions
    When the user reopens the application
    Then the recovery modal should show "3 recordings can be recovered"
    And the modal should list all sessions with details
    When the user selects "Recover All"
    Then all sessions should be processed sequentially
    And each should be uploaded or saved locally
    And all recovered recordings should appear in playlist

  Scenario: Partial recovery with corrupted chunks
    Given the user has a crashed recording session
    And some chunks are corrupted in IndexedDB
    When the user clicks the "Recover" button
    Then the system should skip corrupted chunks
    And assemble only valid chunks
    And show a warning about data loss
    And still create a partial recording
    And the recording duration should reflect actual recovered audio

  Scenario: Recovery after system shutdown
    Given the user is recording audio
    And the user records for 30 seconds
    When the computer shuts down unexpectedly
    And the user restarts and opens the application
    Then recovery should work the same as browser crash
    And all chunks saved before shutdown should be recoverable
    And the full 30 seconds should be preserved

  Scenario: Background tab recovery
    Given the user is recording in a background tab
    And the browser kills the tab to free memory
    When the user navigates back to the tab
    Then the application should reload
    And recovery detection should trigger
    And the recording should be recoverable via recovery modal

  Scenario: Recovery cleanup after successful save
    Given the user has recovered a recording
    And the recording was successfully saved
    When the user verifies the recording in the playlist
    Then the recovery_chunks should be deleted automatically
    And IndexedDB storage should be freed
    And no duplicate recovery prompts should appear
