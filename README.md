# rumi-analytica
![Logo](/images/rumi-analytica-logo.png)
Multi-agent analytics platform powered by Gemini and deployed on Cloud Run.

TODO:
+ need to provide discovery Engine Viewer to service account & enable  Cloud Resource Manager API  on the project

## Deployment Guide

Follow these steps to deploy the application to your own Google Cloud project.

### Step 1: Fork and Clone the Repository

1. **Fork** this repository to your own GitHub account by clicking the "Fork" button at the top right of the page.


## Creating Cloud Build Triggers
### Connect GitHub to Google Cloud Build

This one-time setup authorizes your Google Cloud project to access your GitHub repository, which is required for the automated CI/CD pipeline.

**IMPORTANT:** Before accessing a link below, you might be redirected to enable the Cloud Build API. It is fine to enable that API, and then click on the link again.

1.  Navigate to the **[Cloud Build Repositories page](https://console.cloud.google.com/cloud-build/repositories)** in the GCP Console.
2.  Make sure you are in the correct GCP project, then click **Connect repository**.
3.  Select **GitHub (Cloud Build GitHub App)** as the source and click **Continue**.
4.  Authenticate with your GitHub account. You will be redirected to GitHub to **Authorize Google Cloud Build**.
5.  On the next screen, you may be prompted to **Install Google Cloud Build** if it's not already configured for your account. Click the install button and choose which repositories to grant access to (you can select just your forked repo).
6.  You will be redirected back to the GCP console. Select your **GitHub Account** and the forked **Repository** from the dropdown menus.
7.  Check the box to agree to the terms and click **Connect**.