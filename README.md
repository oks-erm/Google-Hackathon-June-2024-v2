# Google-Hackathon-June-2024

---
## How to deploy the project on Google Cloud:
1. Install Google Cloud CLI for your OS: https://cloud.google.com/sdk/docs/install.
   
     (You can check if it's installed by running `gcloud --version` in the terminal.)
3. Update your environment with requirements from the `requirements.txt` file.
4. Activate it according to the OS's instructions.
5. Go to the project's root directory and do the following steps:
    1. Run `gcloud init`. 
    2. Log in with your Google account.  In our case, Oksana owns the project so you need her account to access it.
    3. Choose the project you want to deploy the app to.
6. `cmmod +x ./deploy.sh`
7. Run `deploy.sh` script.

---
### How to stop the server:
1. Check the name of the active service: `gcloud app services list`.
2. Stop the service: `gcloud app services stop SERVICE_NAME`.
