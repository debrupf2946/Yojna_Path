# Yojna _Path
## About

## Vision
## Getting Started
### Setting Up the Environment

1. **Create a Virtual Environment**  
   Navigate to your project directory and create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
    ```

2. **Install Requirements**  
   Install the necessary packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the application, run the following command:

```bash
python3 main.py
```
In another terminal using ngrock make yout local host public using the following command:
```bash
ngrok http 8000
```



### Setting Environment Variables

You need to export the following environment variables:

- `ELEVENLABS_API_KEY`
- `AGENT_ID`

You can do this in your terminal:

```bash
export ELEVENLABS_API_KEY='your_api_key_here'
export AGENT_ID='your_agent_id_here'
```
### Calling Yojna_Path
Connect the ngrock public Webhook to twilio number in twilio console.Then by dialing the number connects to Yojna_Path Agent