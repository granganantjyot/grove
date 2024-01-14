import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './EventsComponent.css';


const EventsComponent = ({ url }) => {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const response = await axios.post('http://localhost:8080/api/get-events', { url });
                setEvents((response.data.events));
            } catch (error) {
                setLoading(false);
                console.error('Error fetching events:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchEvents();
    }, [url]);

    if (loading) {
        return (
            <p>Loading...</p>
        )
    }
    else {
        return (
            <div className='events-container'>
                {events.map((event, index) => (
                    <div className='singular-event-container' key={index}>
                        <p><b>{event.summary}</b></p>
                        <p><b>Start:</b> {event.start}</p>
                        <p><b>End:</b> {event.end}</p>
                    </div>
                ))}
            </div>
        )
    }
};

export default EventsComponent;