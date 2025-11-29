Feature: Connection Loss During Recording
  As a user experiencing unstable internet
  I want recordings to continue seamlessly when connection is lost
  So that I don't lose any recorded audio

  Background:
    Given the WaveForge Pro application is loaded
    And the user is on the main recording page

  Scenario: Seamless transition from online to offline
    Given the user has an active internet connection
    And the ConnectionMonitor shows "Online" status
    When the user clicks the record button
    And the user records for 3 seconds
    And the internet connection is lost
    Then the ConnectionMonitor should show "Offline" status
    And a toast notification should appear saying "You are now offline"
    And the recording should continue without interruption
    And chunks should continue to be saved locally
    And no upload attempts should be made after connection loss

  Scenario: Save after connection loss during recording
    Given the user started recording while online
    And the connection was lost during recording
    And the user continued recording offline
    When the user stops the recording
    Then the save modal should appear
    And the user should enter a filename
    And client-side assembly should be used
    And the recording should be saved locally
    And the recording should have a "LOCAL" badge

  Scenario: Partial upload handling
    Given the user started recording while online
    And 5 chunks were uploaded successfully
    And the internet connection is lost
    And 3 more chunks are recorded offline
    When the user stops the recording
    Then the system should detect incomplete upload
    And client-side assembly should be used as fallback
    And all 8 chunks should be assembled locally
    And the recording should be saved to IndexedDB

  Scenario: Connection restored during recording
    Given the user started recording while offline
    And the ConnectionMonitor shows "Offline" status
    When the user records for 2 seconds
    And the internet connection is restored
    Then the ConnectionMonitor should show "Online" status
    And a toast notification should appear saying "Back online"
    And new chunks should start uploading
    And previously saved chunks should remain local
    And the recording should continue without interruption

  Scenario: Upload recovery after connection restored
    Given the user has a recording with partial upload
    And the recording has 5 uploaded chunks and 3 local chunks
    When the internet connection is restored
    Then the remaining chunks should be queued for upload
    And the service worker should upload the pending chunks
    And the user can retry the recording completion
    When all chunks are uploaded
    And the user signals recording complete again
    Then server assembly should be triggered
    And the recording should be updated to server-backed

  Scenario: Multiple connection losses during single recording
    Given the user starts recording while online
    When the connection is lost after 5 seconds
    And the connection is restored after 10 seconds
    And the connection is lost again after 15 seconds
    And the user stops recording after 20 seconds
    Then all chunks should be preserved (local or uploaded)
    And client-side assembly should be used as fallback
    And the recording should be complete with all audio data
    And the recording duration should be approximately 20 seconds

  Scenario: Network instability with rapid on/off transitions
    Given the user starts recording while online
    And the network becomes unstable
    When the connection toggles on/off rapidly
    Then the ConnectionMonitor should track each state change
    And toast notifications should inform the user
    And chunks should be saved locally as backup
    And uploads should only occur when connection is stable
    And recording quality should not be affected
