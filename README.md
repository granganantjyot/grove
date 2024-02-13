# Grove

Please note that this project is a work-in-progress.

## What is Grove?
Your one-stop calendar assistant. Manually inputting events into your calendar provider (whether it's Google Calendar, Outlook, or Apple Calendar), can be a hassle.

What if you could give someone your event details, and they could update your calendar for you? That's exactly what Grove does.

You can give Grove prompts for your events. For example: "GitHub internship interview next Monday from 9:30am to 10:15am". Grove takes away the pain-staking process of entering event details one-by-one.

Grove generates an editable ICS calendar feed that you can subscribe to from any calendar client.

## How Can I Use It?
You can try out Grove [here](https://d3c1t09rjq982a.cloudfront.net)

Please note that there is a lot more planned for this project, and it is a WIP.


## Tech Stack
Python/Flask backend with React frontend. The custom NLP model was created with spaCy.

## Notes
- The custom NLP model is in its early stages. Refinements will be made in the near future.
- ICS feeds work best with Apple Calendar since it can fetch new events the quickest compared to other options like Google Calendar and Outlook.
- There is a lot more planned for this project. Stay tuned.
