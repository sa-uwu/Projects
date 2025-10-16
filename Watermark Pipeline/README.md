<h1 align="center">🖼️ Watermark Pipeline </h1>

<p align="center">⭐ ⭐ ⭐</p>


<br>

It all started one fine day when I was struggling to remove a watermark from an image I wanted to use. That’s when I thought, 
>**"if removing a watermark is this hard, how difficult is it to apply one? 🤔"**
<br>

Organizations and individuals publish hundreds of photographs, diagrams, and visuals in their articles, and of course, they wouldn’t want someone like me to just reuse them so easily 😛. But then another question hits me:


>**How long does it take to watermark a single image?**  
10 minutes? 5 minutes? Maybe 3?  

I definitely wouldn’t want to spend that much time manually processing a single image, let alone hundreds of them 🤯.

That’s when an idea struck me 💡

<br>

<p align="center">
  <img src="https://media1.tenor.com/m/OSviYqOqvOMAAAAC/automation-audio-engineer.gif" width="500">
</p>

And that’s how this small automation project came to life 🚀.

<br>




## 📌 Project Overview  

The **Watermark Pipeline** automates the process of applying watermarks to images.

- User needs to upload images through an APIGW to an S3 bucket.  

- As soon as an image is uploaded, the pipeline automatically triggers the Lambda Function to process the image and store back.

- Once the image is processed and uploaded, another Lambda is invoked that generates a presigned url and leverages SES to send it back to user via email. 

This automated workflow not only reduces the **time**, but it make the task **easy and scalable**, even for large volumes of images.

<br>

![](https://github.com/sa-uwu/Projects/blob/main/Watermark%20Pipeline/assets/workflow.gif)

<br>

<br>

<p align="center">
  <img src="https://media1.tenor.com/m/ky1fjuAVWQgAAAAC/boredmemes-bayc.gif" width="200">
</p>
<br>

<p align="center">
  <strong>Enough of talking. Let's get our hands dirty and build it together!</strong>
</p>

<br>


<br>

---

### Prerequisites 🛠️

---
<br>

<span style="color:#007acc;font-weight:bold;"> 

a. AWS Account  
b. Access to following Services.        
 - **Lambda**    
 - **API Gateway**
 - **Simple Storage Service (S3)**
 - **Identity and Access Management (IAM)**  
 - **EventBridge** 
 - **Simple Email Service (SES)**   

c. Email id (preferably two).  
d. Postman application

 </span> 
 <br>

---

### 1. Creating an S3 Bucket 
---
<br>

For this project, we can either use **two separate S3 buckets** or create **two separate folders** within a single bucket.  

- The first location is for uploading the **raw images**.  
- The second location is for storing the **processed images**.  

We will be using the **'folder approach'** and create two  folders within a single bucket for simplicity and easier management.
<br>

#### Refer the below image for S3 Bucket configuration
[<img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/s3/BucketConfig.png" width="300">](https://github.com/sa-uwu/Projects/blob/main/Watermark%20Pipeline/assets/s3/BucketConfig.png)

<br> 

#### Once the bucket is created, click the **'Create Folder'** button and create two folders named **`raw`** and **`processed`**.

![s3 folders](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/s3/S3Folders.png)

<br>

> ### **Fun Fact about S3 💡** 
>
> Amazon S3 is an **object storage service**, which means it does not have real folders or files.  
>
> Everything in S3 is treated as an **individual object**. For example:  
> - `raw/test1.png` is an object with actual data  
> - `raw/` is just an empty object, with key name ending with ' / '
> 
> The `folder/file` hierarchy you see in the AWS console is just a **user-friendly representation**, designed to match how humans think about organizing data.


<br>

---

### 2. Configuring IAM Roles
---
<br>

IAM allows **users, services,** and **applications** to assume roles and perform specific actions on AWS resources.  

For this project, we need to configure IAM roles for both **Lambda** and **API Gateway**.  
<br>

- Create the IAM role for **API Gateway `APIGW-S3-Uploads`** as shown below:  

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/gifs/APIGW%20Role.gif" alt="API Gateway IAM Role" width="600">
  </p>

<br>

> **Best Practice Reminder ‼️**  
>
> In the real-world scenario, one should always follow the principle of **least-privilege**, and configure and grant fine-grained permissions that are absolutely necessary.
> 
>
<br>

* Adhering to the principle of **least-privilege**, I have created a custom, fine-grained permission policy that will be attached to the **API Gateway IAM role `APIGW-S3-PutObject`**.
<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/gifs/APIGW-InlinePolicy.gif" alt="API Gateway IAM Role" width="600">
  </p>
<br>

* **Custom Permission Policy**

``` JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3Put",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectTagging"
            ],
            "Resource": [
              "arn:aws:s3:::{BucketName}/raw",
              "arn:aws:s3:::{BucketName}/raw/*"
            ]
        }
    ]
}
```
---
<br>

 Following similar steps, we will create two additional IAM Roles, **`LambdaWaterMarkProcessor`** and **`LambdaWaterMarkEmail`** for our **Lambda Functions** and attach below inline policies.

<br>

- **Inline policy for `LambdaWaterMarkProcessor`**
<a name="LambdaProcessor"></a>


``` JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaToGetRawImages",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectTagging"
            ],
            "Resource": [
                "arn:aws:s3:::{BucketName}/raw/",
                "arn:aws:s3:::{BucketName}/raw/*"
            ]
        },
        {
            "Sid": "AllowLambdaToPutProcessedImages",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectTagging"
            ],
            "Resource": [
                "arn:aws:s3:::{BucketName}/processed/",
                "arn:aws:s3:::{BucketName}/processed/*"
            ]
        }
    ]
}

```
<br>

- **Inline policy for `LambdaWaterMarkEmail`**


```JSON 
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GetObject",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectTagging"
            ],
            "Resource": [
                "arn:aws:s3:::{BucketName}/processed/",
                "arn:aws:s3:::{BucketName}/processed/*"
            ]
        },
        {
            "Sid": "SendEmail",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail"
            ],
            "Resource": [
                "arn:aws:ses:{region}:{Account ID}:identity/abc@gmail.com",
                "arn:aws:ses:{region}:{Account ID}:identity/123@gmail.com"
            ]
        }
    ]
}

```
<br>

---

<br>

#### Once completed, your IAM role should appear as below:

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Images/LambdaProcessorIAM.png" alt=" Lambda Processor IAM Role" width="600">
  </p>  
<h4 align="center"> LambdaProcessorIAM </h4>
<a name="LambdaProcessor"></a>

<br>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Images/LambdaEmailIAM.png" alt=" Lambda Processor IAM Role" width="600">
  </p>
  
<h4 align="center"> LambdaWaterMarkEmail </h4>
<a name="LambdaEmail"></a>

<br>

---
### 3. Creating an API Gateway.

---

<br>

An **API Gateway** serves as the central entry point for client requests, acting as an intermediary between clients and backend services. 

It also manages critical aspect such as **request and response handling**, **traffic management** (`routing`, `throttling`, `caching`) and **security enforcement**( `authentication` and `authorization`).

By offloading these operational tasks, API Gateway handles much of the infrastructure complexity, enabling developers to focus on building scalable and efficient backend services.
<br>

> [!Note]
>
>API Gateway is a powerful but complex service, with many configuration options around integrations, security, throttling, and request handling.
>
> Explaining its detailed configuration would take unnecessary time and is outside the scope of this project. Instead, I’ve included images and GIFs that provide a clearer picture of the API Gateway configuration and how it fits into the pipeline. 
>
> Please refer to those visuals for a better understanding. 
>
> 
<br>

---

#### 🚶‍♂️Follow the steps below create an API

1. Navigate to the **API Gateway Console**.
2. Click on **Create API**.
3. Select **REST API**.
4. Enter a meaningful **API Name**.
5. Leave the remaining settings as **default**.
6. Click **Create API**.

<br>

 Once an API is created, click on **Create resource** and add resource named ``{Bucket}``

Then, create another resource under `{Bucket}` named `{Filename}`.

- Next, follow the image below to configure a ``PUT`` method under `{Filename}` resource.

![method create](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/APIGW%20Method.png)

You can uncheck ``API key required`` under **Method request settings** for simplicity matters and skip [**Setting up Usage plan and API Keys**](#configuring-usag-plan-and-api-keys) section.

</br>

- Your **Method Request** configuration should look like the example shown below:
<br>

![method request](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/MethodRequestConfig.png)

<br>

---

<br>

- Next, navigate to **Integration Request** for the ``PUT`` method and configure the settings as shown below.

![method request](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/IntegrationRequest.png)

<br>

<br>

---
### 3.1. Configuring Binary Media Type.  

---

<br>

1. Navigate to your API console.
2. In the left panel select **'API settings'**.
3. Scroll down and click on **'Manage media types'**
4. Add `image/jpg` and `image/png` as Binary Media Type and save.

<br>

>Binary Media Types essentially tells API Gateway how to handle files (like images or PDFs) correctly instead of treating them as text.

<br>

---
### 3.2. Setting up Usage plan and API Keys.  
<a name="configuring-usag-plan-and-api-keys"></a>

---
<br>

What’s more important than building **scalable** AWS infrastructure is having a **secure** AWS infrastructure. 

You don’t want malicious users spamming your API and making your AWS bill go brrrrr 📈 🚀

<p align="center">
  <img src="https://x.com/_lhermann/status/1742808088980160849/photo/1" width="700">
</p>


This is where **API Keys** come into play.

They help control and secure access to your API by ensuring only clients with a valid key can use specific methods.

When combined with usage plans, API keys let you enforce rate limits, quotas, and burst limits, protecting your backend from overuse and managing API consumption effectively.

🔑 **Creating API Keys**


1. On API Gateway Console, navigate to `API Keys`
2. Click **Create API key**
3. Enter a meaningful **Key Name**.
4. Set `API Key` → Auto Generate ✅ → and click **Save**

<br>

> [!Important]
>After creating the API key, you need to associate it with a **Usage Plan** to enforce throttling and quota limits.

<br>



**⚙️ Configuring Usage Plan**


1. On API Gateway Console, navigate to `Usage Plan`
2. Click **Create usage plan**
3. Enter a meaningful **Name**.
4. Configure **Throttling**:
   - **Rate** = x
   - **Burst** = Rate × 3 ✅ <br>       
5. Under **Quota**, specify the total number of requests to the api allowed within the selected time period (day, week, or month).



<br>

> [!NOTE]
>
>Ideally, the **Burst** value should be **2–5× your Rate**.  
> For example, if your Rate is 10 requests/sec, a Burst of 20–50 is recommended.  
> This allows short spikes of traffic without overwhelming your backend.

<br>

> [!IMPORTANT]
>
> Once the **Usage Plan** is created, make sure to associate your `API Stage` and `API Keys` so that the throttling and quota settings take effect.


#### **Once configured, your API is ready to be deployed to a new stage..**

<br>

---
### ✅ Testing API using Postman

<a name="testingAPI"></a>



---
<br>
Before moving forward, let’s verify that the API works as expected using Postman.

<br>

1. In the API Gateway Console, go to the **Stages** section and copy the Invoke URL for your deployed stage. 

    Example:
    `https://.execute-api.us-east-1.amazonaws.com/dev1/{Bucket}/{Filename}`


2. Open Postman, select the `PUT` method, and paste the Invoke URL.

3. Replace the placeholders:    
    +   **{Bucket}** → your S3 bucket name
    +   **{Filename}** → desired file name for the image

    Example:
    `https://{api id}.execute-api.us-east-1.amazonaws.com/dev1/mywatermarkbucket.us-e-1/test1`

4. Under **'Authorization'** choose `API Key`as auth type.  
    + **Key**: `x-api-key`
    + **value**: your actual API key value from the API Gateway console
    + **Add to**: `Header`
5. Go to **Body** → select **Binary** → click **Select File** and upload an image from your local system.
6. In the Headers tab, ensure the following are present with their values:
    + `x-api-key` → your actual API key value from the API Gateway console
    + `Content-Type` → image/png or image/jpg
7. Add one more header:
    + **Key**: `x-amz-tagging`
    + **Value** `text=wayne%enterprises&size=large&position=Top-right&color=Grey&Email=receiver@gmail.com`
8. Click **Send** and confirm that the response returns a `200 OK` status code.
9. Open your S3 bucket and check the `raw/` folder to confirm that the image has been uploaded with the correct tags.


<br>

---
<br>

<h3 align="center">😮‍💨 Phew... that was a lot of steps!</h3>

<br>

<h4 align="center">But hang on </h4>

<p align="center">
  <img src="https://media1.tenor.com/m/KQDte4i0o50AAAAC/crawling-back.gif" width="500">
</p>

<br>

---
### 4. Creating SES Identity

---

For this project we need two email addresses.
+ **Sender**
+ **Receiver** 

<br>

Follow below steps to configure SES Identities.

1. Navigate to the Amazon SES Console.
2. Under Identities, click Create identity.
3. Choose Email address, enter a valid email, and create the identity.
4. Check your inbox, you will receive a verification email from Amazon SES.
Click the verification link to confirm.  
📸 See the screenshot below for reference.

5. Repeat the same steps for the second email address.

<br>

>💡 Once verified, you can send messages between these two addresses.

>📬 Check your spam folder if the verification mail doesn’t show up!

<br>

### ✨ Now that all the pieces are in place, let’s move on to configuring and deploying Lambda functions!

<br>

----
### 5. Deploying Lambda functions

---

#### **5.1 **

1. Navigate to the Lambda console and click **Create Function**
2. Configure the function as follows:
    + Name: **`LambdaImageProcessor`**
    + Architecture: **x86_64**
    + Runtime: **Python 3.10**
    + Execution Role: [**LambdaWaterMarkProcessor↗️**](#lambdaprocessor) (configured earlier)

    (You can also refer to the GIF below for visual guidance)

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/gifs/Deploying%20Lambda%20Function.gif" alt="LambdaFunction" width="700">
  </p>

<br>

3. Deploy Function Code:
    + Refer to the [**function code↗**](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Function%20code/LambdaImageProcessor/lambda_function.py) and deploy Lambda function.

4. Add Pillow Layer:
    + Navigate to **Code** → **Add Layer** and enter the following Layer ARN:

         `arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p310-Pillow:9`

>[!Note]

Incase, you are using a different python version, refer [**Klayers Github repository↗**](https://github.com/keithrozario/Klayers/tree/master/deployments) as suggested in AWS [**re:Post↗**](https://repost.aws/questions/QU11QL_JaISAOSykJteHyFHg/issue-with-importing-pillow-library-for-image-processing-in-aws-lambda-environment#:~:text=Hi%2C%20Pillow%20is%20packaged%20as%20a%20standard%20Lambda%20layer.).

5. Set Environment Variables:
    + Under **Configuration** section → Environment Variables
        + **`Key: OutputBucket`**
        + **`Value: {Your S3 Bucket Name}`**
6. Adding S3 trigger:
    + Click on **Add trigger**
    + Select **S3 Bucket** as a source
    + Select `PUT` as event type 
    + `raw/` prefix
    + Acknowledge the warning and click **Add**

    (refer to the GIF below for visual guidance)

    <p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/gifs/Lambda%20S3%20trigger.gif" alt="LambdaFunction" width="700">
  </p>


---
<br>

#### **5.2 `LambdaWaterMarkEmail`**

1. Navigate to the Lambda console and click **Create Function**
2. Configure the function as follows:
    + Name: **`LambdaWaterMarkEmail`**
    + Architecture: **x86_64**
    + Runtime: **Python 3.10**
    + Execution Role: [**LambdaWaterMarkEmail↗**](#lambdaemail) (configured earlier)

3. Deploy Function Code:
    + Refer to the [**function code↗**](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Function%20code/LambdaWaterMarkEmail/lambda_function.py) and deploy Lambda function.
    ```
    LambdaImageProcessor/
    │
    ├── lambda_function.py
    ├── email_template.html
    └── email_template.txt
    ```
4. Set Environment Variables:

    |    **Key**        |      **Value**          |
    | ----------------- | ----------------------- |
    | **OutputBucket**  |  **{YourS3BucketName}** |
    | **SENDER_EMAIL**  |  **sender@gmail.com**   |

<br>

5. Adding S3 trigger:
    + Click on **Add trigger**
    + Select **S3 Bucket** as a source
    + Select `PUT` as event type 
    + `processed/` prefix
    + Acknowledge the warning and click **Add**

<br>

<br>

---

<h1 align="center"> Testing the pipeline </h1>

<br> 

Now that all the building blocks of this pipeline are in place, let's upload another image through the API Gateway URL.

1. Navigate to Postman and follow the steps peroformed earlier while [**testing api↗**](#testingapi)

2. Navigate to your S3 bucket and check the `raw/` folder to confirm that the uploaded image is present.

3. Check the `processed/` folder to ensure that the watermarked (or processed) image has been uploaded successfully.

4. Open the receiver email inbox configured in your pipeline. An email with the subject **"Your Watermarked Image is Ready!"** will be waiting for you.

<br>

>[! NOTE]:
>(check the spam/junk folder if not found).

5. The email contains a presigned URL embedded in the "View Image" and "Download Image" buttons. Click either button to access your processed image.

>[! NOTE]:
> The presigned URL is valid for 1 hour (60 minutes) from the time the email is received.


---
<h1 align="center">  Documentation is being refined. Apologies for the inconvinence 🙏 </h1>


<p align="center">
  <img src="https://media.tenor.com/dAGxcNtm40kAAAAi/construction-work-in-progress.gif" width="500">
</p>

