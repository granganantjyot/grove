import React, { useState } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import './InputComponent.css';
import { FiArrowUpCircle } from "react-icons/fi";
import toast from 'react-hot-toast';

const InputComponent = ({ onPromptSubmit }) => {
    const [prompt, setPrompt] = useState('');

    const handleInputChange = (e) => {
        setPrompt(e.target.value);
    };

    const handlePromptSubmit = async () => {

        // Check uuid to determine if user is new or existing
        let uuid = localStorage.getItem("grove-uuid");
        let newUser = false;

        if (!uuid) {
            uuid = uuidv4();
            localStorage.setItem("grove-uuid", uuid);
            newUser = true;
        }

        // POST request to backend
        try {
            setPrompt('');
            let tz = Intl.DateTimeFormat().resolvedOptions().timeZone;

            // Loading toast
            toast.loading('Loading...', {position: 'bottom-center',});

            const response = await axios.post('http://localhost:8080/api/process_prompt', { "prompt": prompt, "user": { "uuid": uuid, "new_user": newUser, "timezone": tz } });

            // Dismiss loading toast
            toast.dismiss()

            // No event detected
            if (!response.data.result.success){
                // Restore user's input
                setPrompt(prompt);
            }
            onPromptSubmit(response.data.result.success);
        }
        catch (error) {
            onPromptSubmit(false);
            console.log('Error:', error);
        }
    };

    return (
        <div className="fixed-input-container">
            <input
                type="text"
                value={prompt}
                placeholder="Try &quot;Job interview this Thursday from 9am to 10:30am&quot;"
                onChange={handleInputChange}
                className="rounded-input"
                // Check for enter key pressed
                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        handlePromptSubmit();
                    }
                }}
            />
            <FiArrowUpCircle className='submit-icon' onClick={handlePromptSubmit} />
        </div>

    )
}
export default InputComponent;