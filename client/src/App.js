import InputComponent from './InputComponent/InputComponent';
import TitleComponent from './TitleComponent/TitleComponent';
import FeedLinkComponent from './FeedLinkComponent/FeedLinkComponent';
import EventsComponent from './EventsComponent/EventsComponent';
import toast, { Toaster } from 'react-hot-toast';
import React from 'react'
import './App.css';

function App() {

  // Handling prompt submission
  const handlePromptSubmit = (success) => {
    if (success){
      toast.success("Event created", {position: 'bottom-center',});
      setTimeout(function(){
        window.location.reload(false);
    }, 1000);
    }
    else{
      toast.error("Event could not be detected", {position: 'bottom-center',});
    }
  }


  let content = <p>An error occurred. Try again later.</p>

  // Check if user is new or existing
  let uuid = localStorage.getItem("grove-uuid");
  // New user
  if (uuid == null){
    content = (
      <div>
        <p id='calendar-title'>Yikes! Your calendar seems uneventful.</p>
        <p>Add an event below to get started.</p>
      </div>
    )
  }
  // Existing user
  else{
    content = (
      <div>
        <p id='calendar-title'>Your Calendar Feed:</p>
        <FeedLinkComponent url={getFeedURL(uuid)}></FeedLinkComponent>
        <p id='events-title'>Your Events:</p>
        <EventsComponent url={getFeedURL(uuid)}></EventsComponent>
      </div>
    )
  }



  return (
    <div className="App">
      <center>
        <TitleComponent></TitleComponent>

        <div className='content-container'>
          {content}
        </div>

        <InputComponent onPromptSubmit={handlePromptSubmit} />
        <Toaster />
      </center>
      </div>);
}
function getFeedURL(uuid){
  return "https://grove-calendar.s3.us-east-2.amazonaws.com/ics/" + uuid + ".ics";
}
export default App;
