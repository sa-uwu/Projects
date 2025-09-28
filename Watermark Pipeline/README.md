# 🖼️ Watermark Pipeline 

It all started one fine day when I was struggling to remove a watermark from an image I wanted to use. That’s when I thought, 
>**"if removing a watermark is this hard, how easy is it to apply one? 🤔"**
<br>

Organizations and individuals publish hundreds of photographs, diagrams, and visuals in their articles, and of course, they wouldn’t want someone like me to just reuse them so easily 😛. But then another question hit me:


>**How long does it take to watermark a single image?**  
10 minutes? 5 minutes? Maybe 3?  

I definitely would not want to spend that much time on one image, let alone hundreds of them 🤯. 

That is when an idea struck me:  
<br>

<p align="center">
  <img src="https://media1.tenor.com/m/OSviYqOqvOMAAAAC/automation-audio-engineer.gif" width="500">
</p>

And that is how this small project came to life 🚀.  

---

<br>


## 📌 Project Overview  

The **Watermark Pipeline** automates the process of applying watermarks to images.

- User needs to upload images through an APIGW to an S3 bucket.  

- As soon as an image is uploaded, the pipeline automatically triggers the Lambda Function to process the image and store back.

- Once the image is processed and uploaded, another Lambda is invoked that generates a predigned url and leverages SES to send it back to user via email. 

This automated workflow not only reduces the **time**, but it make the task **easy and scalable**, even for large volumes of images.

<br>

![](https://github.com/sa-uwu/Projects/blob/main/Watermark%20Pipeline/assets/workflow.gif)

<br>


<h1 align="center">⚙️ Getting Started</h1>

---

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

### 🛠️ Prerequisites

#### a. AWS Account
#### b. Access to following Services 
  *  Lambda
  *  API Gateway
  *  Simple Storage Service (S3)
  *  Identity and Access Management (IAM)
  *  EventBridge
  *  Simple Email Service (SES)
#### c. Email id (preferably two)

<br>

### 1. Creating an S3 Bucket 
---


For this project, we can either use **two separate S3 buckets** or create **two separate folders** within a single bucket.  

- The first location is for uploading the **raw images**.  
- The second location is for storing the **processed/final images**.  

In this project, we are using the **folder approach** within a single bucket for simplicity and easier management.
<br>

#### Refer the below image for S3 Bucket configuration
[<img src="https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/s3/s3bucket%20config.png" width="300">](https://github.com/sa-uwu/Projects/blob/main/Watermark%20Pipeline/assets/s3/s3bucket%20config.png)

<br> 

#### Once the bucket is created, click the **'Create Folder'** button and create two folders named **'raw'** and **'final'**.

![s3 folders](https://raw.githubusercontent.com/sa-uwu/Projects/main/Watermark%20Pipeline/assets/s3/s3%20folders.png)


<br>

#####  💡 Fun Fact about S3

> #####  Amazon S3 is an **object storage service**, which means it does not have real folders or files.  
> #####  Everything in S3 is treated as an **individual object**. For example:  
> #####  - `/folder/file1.txt` is an object with actual data  
> #####  - `/folder/` is just an empty object, with key name ending with '/'.
> 
> #####  The `folder/file` hierarchy you see in the AWS console is just a **user-friendly representation**, designed to match how humans think about organizing data.
    
