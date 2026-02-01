let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = uploadAudio;

        mediaRecorder.start();
        document.getElementById('recordBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('status').innerText = "Recording...";
    } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Could not access microphone.");
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
        mediaRecorder.stop();
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('status').innerText = "Processing...";
    }
}

async function uploadAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "recording.webm");
    
    // Get session/question info from hidden fields or URL
    const sessionId = document.getElementById('session_id').value;
    const questionNumber = document.getElementById('question_number').value;

    try {
        const response = await fetch(`/practice/${sessionId}/answer/${questionNumber}`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('status').innerText = "Saved!";
            document.getElementById('nextBtn').disabled = false;
            console.log(result);
        } else {
            document.getElementById('status').innerText = "Upload failed.";
        }
    } catch (err) {
        console.error("Upload error:", err);
        document.getElementById('status').innerText = "Error uploading.";
    }
    
    // Reset chunks for next recording
    audioChunks = [];
}

function nextQuestion() {
    let currentNum = parseInt(document.getElementById('question_number').value);
    
    if (currentNum < 5) {
        currentNum++;
        
        // Update State
        document.getElementById('question_number').value = currentNum;
        
        // Update UI
        document.getElementById('question-title').innerText = `Question ${currentNum}`;
        document.getElementById('question-text').innerText = questionsData[currentNum.toString()];
        
        // Reset Recording UI
        document.getElementById('status').innerText = "Ready to record.";
        document.getElementById('recordBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('nextBtn').disabled = true;
        
        if (currentNum === 5) {
            document.getElementById('nextBtn').innerText = "Finish Exam";
        }
    } else {
        // Finish Exam
        const sessionId = document.getElementById('session_id').value;
        window.location.href = `/review/${sessionId}`;
    }
}
