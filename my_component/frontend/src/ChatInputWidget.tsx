import React, { useState, useEffect, useCallback } from "react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import { useReactMediaRecorder } from "react-media-recorder";
import SendIcon from "@mui/icons-material/Send";
import MicIcon from "@mui/icons-material/Mic";
import StopIcon from "@mui/icons-material/Stop";
import './ChatInputWidget.css';

const ChatInputWidget: React.FC = () => {
  const [inputText, setInputText] = useState<string>("");
  const [isRecording, setIsRecording] = useState<boolean>(false);

  const {
    startRecording,
    stopRecording,
    mediaBlobUrl,
  } = useReactMediaRecorder({ audio: true });

  useEffect(() => {
    Streamlit.setFrameHeight(650);  // Set component height
  }, []);

  const sendDataToStreamlit = (data: any) => {
    Streamlit.setComponentValue(data);
  };

  const sendAudioBlobAsBytes = useCallback((audioBlob: Blob) => {
    audioBlob.arrayBuffer().then(buffer => {
      const audioArray = Array.from(new Uint8Array(buffer));  // Convert ArrayBuffer to array of bytes
      sendDataToStreamlit({ audioFile: audioArray });  // Send as audioFile in binary format
    });
  }, []);

  const fetchAudioAndSend = useCallback(async () => {
    if (mediaBlobUrl) {
      const response = await fetch(mediaBlobUrl);
      const audioBlob = await response.blob();
      sendAudioBlobAsBytes(audioBlob);
      setIsRecording(false);  // Stop recording after sending
    }
  }, [mediaBlobUrl, sendAudioBlobAsBytes]);

  useEffect(() => {
    if (mediaBlobUrl) {
      fetchAudioAndSend();
    }
  }, [mediaBlobUrl, fetchAudioAndSend]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputText(event.target.value);
  };

  const handleIconClick = () => {
    if (inputText.trim().length > 0) {
      sendDataToStreamlit({ text: inputText });
      setInputText("");
    } else {
      if (isRecording) {
        stopRecording();
        setIsRecording(false);
      } else {
        startRecording();
        setIsRecording(true);
      }
    }
  };

  return (
    <div className="chat-container">
      <input
        type="text"
        className="chat-input"
        placeholder="Type a message..."
        value={inputText}
        onChange={handleInputChange}
      />
      <button className="icon-btn" onClick={handleIconClick}>
        {inputText.trim().length > 0 ? (
          <SendIcon />
        ) : isRecording ? (
          <StopIcon />
        ) : (
          <MicIcon />
        )}
      </button>
    </div>
  );
};

export default withStreamlitConnection(ChatInputWidget);
