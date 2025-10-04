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

<h3><span style="color:#007acc;font-weight:bold;"> Prerequisites </span> 🛠️</h3>



a. AWS Account  
b. Access to following Services 
- Lambda
- API Gateway
- Simple Storage Service (S3)
- Identity and Access Management (IAM)
- EventBridge
- Simple Email Service (SES)      

c.  Email id (preferably two)

<br>

### 1. Creating an S3 Bucket 
---


For this project, we can either use **two separate S3 buckets** or create **two separate folders** within a single bucket.  

- The first location is for uploading the **raw images**.  
- The second location is for storing the **processed images**.  

We will be using the **'folder approach'** and create two  folders within a single bucket for simplicity and easier management.
<br>

#### Refer the below image for S3 Bucket configuration
[<img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/s3/BucketConfig.png" width="300">](https://github.com/sa-uwu/Projects/blob/main/Watermark%20Pipeline/assets/s3/BucketConfig.png)

<br> 

#### Once the bucket is created, click the **'Create Folder'** button and create two folders named **`raw`** and **`final`**.

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

#### Once completed, your IAM role should appear as below:

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Images/LambdaProcessorIAM.png" alt=" Lambda Processor IAM Role" width="600">
  </p>  

<h4 align="center"> LambdaProcessorIAM </h4>

<br>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/Lambda/Images/LambdaEmailIAM.png" alt=" Lambda Processor IAM Role" width="600">
  </p>
  
<h4 align="center"> LambdaWaterMarkEmail </h4>

<br>


### 3. Creating an API Gateway.

<br>

An **API Gateway** serves as the central entry point for client requests, acting as an intermediary between clients and backend services. 

It also manages critical aspect such as **request and response handling**, **traffic management** (`routing`, `throttling`, `caching`) and **security enforcement**( `authentication` and `authorization`).

By offloading these operational tasks, API Gateway handles much of the infrastructure complexity, enabling developers to focus on building scalable and efficient backend services.
<br>

> ### ✍️ Note:
>
>API Gateway is a powerful but complex service, with many configuration options around integrations, security, throttling, and request handling.
>
> Explaining its detailed configuration would take unnecessary time and is outside the scope of this project. Instead, I’ve included images and GIFs that provide a clearer picture of the API Gateway configuration and how it fits into the pipeline. 
>
> Please refer to those visuals for a better understanding. 
>
> 
<br>

#### 🚶‍♂️Follow the steps below create an API

1. Navigate to the **API Gateway Console**.
2. Click on **Create API**.
3. Select **REST API**.
4. Enter a meaningful **API Name**.
5. Leave the remaining settings as **default**.
6. Click **Create API**.

<br>

 Once an API is created, click on **Create resource** and add resource named ``{Bucket}``

- Next, follow the image below to configure a ``PUT`` method under ``{Bucket}`` resource.

![method create](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/APIGW%20Method.png)

You can uncheck ``API key required`` under **Method request settings** for simplicity matters and skip configuring the API keys sections.

</br>

- Your **Method Request** configuration should look like the example shown below:
<br>

![method request](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/MethodRequestConfig.png)

<br>

- Next, navigate to **Integration Request** for the ``PUT`` method and configure the settings as shown below.

![method request](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/API%20Gateway/Images/IntegrationRequest.png)

#### 

<br>

***

<h1 align="center">  Documentation is being refined. Apologies for the inconvinence 🙏 </h1>


<p align="center">
  <img src="https://media.tenor.com/dAGxcNtm40kAAAAi/construction-work-in-progress.gif" width="500">
</p>

   