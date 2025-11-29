Feature: UI Indicators and User Feedback
  As a user of WaveForge Pro
  I want clear visual feedback about system status
  So that I understand what's happening with my recordings

  Background:
    Given the WaveForge Pro application is loaded

  Scenario: Connection status indicator
    Given the user has internet connection
    Then the ConnectionMonitor should display "Online"
    And the indicator should be in green color
    When the connection is lost
    Then the ConnectionMonitor should display "Offline"
    And the indicator should be in red color
    And a toast notification should appear

  Scenario: Server badge on recordings
    Given the user has recorded audio online
    And the recording was assembled on the server
    When the recording appears in the playlist
    Then a "☁ SERVER" badge should be visible
    And the badge should have a distinctive color
    And the badge should indicate server-backed storage

  Scenario: Local badge on recordings
    Given the user has recorded audio offline
    And the recording was assembled on the client
    When the recording appears in the playlist
    Then a "💾 LOCAL" badge should be visible
    And the badge should have a different color than server badge
    And the badge should indicate local storage

  Scenario: Upload button visibility for local recordings
    Given the user has a local recording in the playlist
    Then an upload button should be visible for that recording
    And the button should be clearly labeled
    When the user has a server-backed recording
    Then no upload button should be visible for that recording

  Scenario: Recording in progress indicator
    Given the user clicks the record button
    Then the record button should change appearance
    And a recording indicator should pulse or animate
    And the elapsed time should update every second
    And the stop button should be enabled

  Scenario: Toast notifications for connection changes
    Given the user is using the application
    When the connection changes from online to offline
    Then a toast notification should appear
    And the message should say "You are now offline"
    And the toast should auto-dismiss after 5 seconds
    When the connection is restored
    Then a toast notification should say "Back online"
    And the toast should use a different color (success)

  Scenario: Upload progress indicator
    Given the user has a local recording
    When the user clicks the upload button
    Then a progress bar should appear
    And the progress should update as chunks upload
    And the percentage should be displayed
    And an estimated time remaining should show

  Scenario: Save modal for offline recordings
    Given the user recorded offline
    When the user stops the recording
    Then a modal dialog should appear
    And the modal should have a filename input field
    And a save button should be present
    And a cancel button should be present
    And the filename should have a default value

  Scenario: Assembly progress for long recordings
    Given the user recorded a 60-minute audio offline
    When the user stops and saves the recording
    Then an assembly progress indicator should appear
    And the progress should show percentage complete
    And a message should explain "Assembling recording..."
    And the user should not be able to start new recording until complete

  Scenario: Download progress indicator
    Given the user clicks download on a large recording
    Then the browser's native download should start
    And the filename should be clear and descriptive
    And the file type should be indicated (.webm)

  Scenario: Error notifications
    Given an error occurs during upload
    When the upload fails
    Then an error toast should appear
    And the message should be user-friendly
    And the toast should not auto-dismiss
    And a retry button should be available

  Scenario: Playback UI feedback
    Given the user clicks play on a recording
    Then the play button should change to pause icon
    And the timeline should show current position
    And the current time should update smoothly
    And the waveform should highlight played portion

  Scenario: Empty playlist state
    Given the user has no recordings
    When the playlist is displayed
    Then a helpful message should appear
    And the message should guide user to record
    And an icon or illustration should make it friendly

  Scenario: Loading states
    Given the application is loading recordings from IndexedDB
    Then a loading spinner should be visible
    And the spinner should indicate progress
    When loading is complete
    Then the spinner should disappear
    And the recordings should render

  Scenario: Batch operation feedback
    Given the user has 10 recordings
    When the user selects "Upload All"
    Then a batch progress indicator should appear
    And it should show "Uploading 3 of 10"
    And individual recording status should update
    And an overall percentage should be displayed
