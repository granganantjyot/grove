import React from 'react';
import { FaClipboard } from 'react-icons/fa';
import './FeedLinkComponent.css';
import toast from 'react-hot-toast';

const FeedLinkComponent = ({ url }) => {
    const handleCopyToClipboard = () => {
        navigator.clipboard.writeText(url);
        toast.success("Copied", {position: 'top-right',});
    };

    return (
        <div className='url-container'>
            <p className="url-text">{url}</p>
            <FaClipboard className="clipboard-icon" onClick={handleCopyToClipboard} />
        </div>
    );
};

export default FeedLinkComponent;