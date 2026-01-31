# Product Requirements Document (PRD): GCSE Chinese Trainer

## 1. Product Overview
The **GCSE Chinese Trainer** is a web-based application designed to assist GCSE Chinese students in practicing for the **Speaking Test (Paper 2)**, specifically targeting the **Higher Tier**. The initial release will focus exclusively on the **Photo Card** component of the exam.

The application leverages AI to simulate the exam environment, providing students with realistic practice scenarios and immediate, actionable feedback on their performance using the Google Gemini AI service.

## 2. Target Audience
*   **Primary Users:** GCSE Chinese students aiming for Higher Tier grades.
*   **Secondary Users:** Teachers or Tutors who may want to review student progress or manage practice content.
*   **Administrators:** System admins managing users and content.

## 3. Scope

### 3.1 In Scope (MVP)
*   **Photo Card Practice Module:**
    *   Simulation of the Photo Card exam section.
    *   Presentation of visual stimuli (photos) and text prompts.
    *   Timed preparation phase.
    *   Audio recording of student answers.
    *   Automated AI feedback and scoring.
*   **User Management:**
    *   User registration and authentication.
    *   Profile management.
*   **Content Management:**
    *   Admin interface to add/edit/delete Photo Card questions.
*   **Review System:**
    *   History of practice sessions.
    *   Playback of recordings.
    *   View AI-generated transcripts and feedback.

### 3.2 Out of Scope (Initial Release)
*   Role-play card practice.
*   General Conversation practice.
*   Reading, Writing, and Listening papers.
*   Teacher-Student classroom linking features.
*   Mobile native app (web responsive only).

## 4. Functional Requirements

### 4.1 Authentication & User Management
*   **FR-01:** Users must be able to sign up and log in (email/password or OAuth).
*   **FR-02:** Users must have a dashboard showing their recent practice activity.

### 4.2 Practice Mode (The Workflow)
*   **FR-03: Selection:** Users can choose to start a "Random Practice" or select a specific topic/card from a library.
*   **FR-04: Preparation Phase:** 
    *   Display the Photo Card and the **first three** known questions.
    *   Provide a timer (simulating the approx. 3 minutes preparation time for Higher Tier).
    *   *Note: Taking notes feature is manual (paper/pen) for the user, as per exam rules, but the app can offer a text area for scratchpad if needed.*
*   **FR-05: Exam Phase:**
    *   The app presents the questions one by one.
    *   **Q1-Q3:** The three questions shown during preparation.
    *   **Q4-Q5:** Two **unseen/unprepared** questions (simulating the examiner's surprise questions).
*   **FR-06: Answering:**
    *   User records their spoken answer for each question via microphone.
    *   Visual indicator for recording status.
    *   Option to re-record (practice mode) or strict one-take (exam mode).

### 4.3 Feedback & Scoring (AI Integration)
*   **FR-07:** Upon session completion, audio recordings are sent to the backend.
*   **FR-08:** The system uses Gemini AI to:
    *   Transcribe the audio to Chinese text.
    *   Evaluate the response based on GCSE Higher Tier criteria (communication, range of language, accuracy).
    *   Provide specific corrections and suggestions for improvement.
*   **FR-09:** Results are saved to the database.

### 4.4 Review & History
*   **FR-10:** Users can view a list of past practice sessions.
*   **FR-11:** Detailed view of a session includes:
    *   The Photo and Questions.
    *   The user's Audio Recording for each question.
    *   The Transcription.
    *   AI Feedback/Score.

### 4.5 Administration
*   **FR-12:** Admins can Create, Read, Update, and Delete (CRUD) Photo Card questions.
*   **FR-13:** A Question entity consists of:
    *   Image file (Photo).
    *   Questions 1-3 (Text, visible during prep).
    *   Questions 4-5 (Text, hidden during prep).
    *   Sample answers or keywords (optional, for AI context).

## 5. Non-Functional Requirements
*   **NFR-01: Performance:** Audio upload and feedback generation should complete within a reasonable time (e.g., < 30 seconds per session).
*   **NFR-02: Usability:** The UI must be clean, distraction-free, and accessible on desktop and tablet devices.
*   **NFR-03: Reliability:** Audio recording must be robust against minor network fluctuations (upload after recording finishes).
*   **NFR-04: Data Privacy:** User recordings and transcripts must be stored securely.

## 6. Data Models

### 6.1 User
*   `id`: Integer (PK)
*   `email`: String
*   `password_hash`: String
*   `created_at`: Datetime
*   `role`: Enum (Student, Admin)

### 6.2 Question (Photo Card)
*   `id`: Integer (PK)
*   `title`: String (e.g., "Family and Relationships Card 1")
*   `image_url`: String (Path to stored image)
*   `question_1`: String (Text)
*   `question_2`: String (Text)
*   `question_3`: String (Text)
*   `question_4`: String (Text - Unseen)
*   `question_5`: String (Text - Unseen)
*   `topic`: String (Theme)
*   `created_at`: Datetime

### 6.3 PracticeSession
*   `id`: Integer (PK)
*   `user_id`: Integer (FK)
*   `question_id`: Integer (FK)
*   `date_taken`: Datetime
*   `total_score`: Integer (Optional, aggregated from AI)

### 6.4 Answer
*   `id`: Integer (PK)
*   `session_id`: Integer (FK)
*   `question_number`: Integer (1-5)
*   `audio_url`: String (Path to stored audio)
*   `transcript`: Text
*   `ai_feedback`: Text
*   `score`: Integer (Optional)

## 7. User Interface Flow
1.  **Login/Dashboard:** User sees "Start Practice" or "Review Past Sessions".
2.  **Setup:** User selects "Random" or a specific topic.
3.  **Preparation Screen:**
    *   Left: The Photo.
    *   Right: Questions 1, 2, 3.
    *   Top: Countdown Timer (12 mins total exam time context, ~3 mins prep).
    *   Action: "Start Exam" button (or auto-start after timer).
4.  **Exam Screen (Question by Question):**
    *   Display Photo (always visible).
    *   Display current Question (e.g., Q1).
    *   Large "Record" button.
    *   "Next Question" button.
5.  **Results Screen:**
    *   Summary of the session.
    *   Loading state while AI processes.
    *   Card-based layout for each Q&A pair showing transcript and feedback.

## 8. Technical Constraints & Dependencies
*   **Frontend:** FastHTML + Materialize CSS.
*   **Backend:** Python (FastHTML/FastAPI).
*   **Database:** PostgreSQL (via FastSQL).
*   **AI Service:** Google Gemini API (Multimodal capabilities for Text/Audio processing).
*   **Storage:** Local filesystem (MVP) or Object Storage (S3/GCS) for audio/images.