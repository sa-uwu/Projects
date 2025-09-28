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
  <img src="https://media1.tenor.com/m/OSviYqOqvOMAAAAC/automation-audio-engineer.gif" width="400">
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


