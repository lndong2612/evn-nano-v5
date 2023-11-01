<div align="center">
  <p>
    <a align="center" href="https://ultralytics.com/yolov5" target="_blank">
      <img width="100%" src="https://raw.githubusercontent.com/ultralytics/assets/main/yolov5/v70/splash.png"></a>
  </p>

[English](README.md) | [简体中文](README.zh-CN.md)
<br>

<div>
    <a href="https://github.com/ultralytics/yolov5/actions/workflows/ci-testing.yml"><img src="https://github.com/ultralytics/yolov5/actions/workflows/ci-testing.yml/badge.svg" alt="YOLOv5 CI"></a>
    <a href="https://zenodo.org/badge/latestdoi/264818686"><img src="https://zenodo.org/badge/264818686.svg" alt="YOLOv5 Citation"></a>
    <a href="https://hub.docker.com/r/ultralytics/yolov5"><img src="https://img.shields.io/docker/pulls/ultralytics/yolov5?logo=docker" alt="Docker Pulls"></a>
    <br>
    <a href="https://bit.ly/yolov5-paperspace-notebook"><img src="https://assets.paperspace.io/img/gradient-badge.svg" alt="Run on Gradient"></a>
    <a href="https://colab.research.google.com/github/ultralytics/yolov5/blob/master/tutorial.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
    <a href="https://www.kaggle.com/ultralytics/yolov5"><img src="https://kaggle.com/static/images/open-in-kaggle.svg" alt="Open In Kaggle"></a>
  </div>
  <br>

YOLOv5 🚀 is the world's most loved vision AI, representing <a href="https://ultralytics.com">Ultralytics</a> open-source research into future vision AI methods, incorporating lessons learned and best practices evolved over thousands of hours of research and development.

We hope that the resources here will help you get the most out of YOLOv5. Please browse the YOLOv5 <a href="https://docs.ultralytics.com/yolov5">Docs</a> for details, raise an issue on <a href="https://github.com/ultralytics/yolov5/issues/new/choose">GitHub</a> for support, and join our <a href="https://ultralytics.com/discord">Discord</a> community for questions and discussions!

To request an Enterprise License please complete the form at [Ultralytics Licensing](https://ultralytics.com/license).

<div align="center">
  <a href="https://github.com/ultralytics" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-github.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://www.linkedin.com/company/ultralytics/" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-linkedin.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://twitter.com/ultralytics" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-twitter.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://youtube.com/ultralytics" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-youtube.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://www.tiktok.com/@ultralytics" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-tiktok.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://www.instagram.com/ultralytics/" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/raw/main/social/logo-social-instagram.png" width="2%" alt="" /></a>
  <img src="https://github.com/ultralytics/assets/raw/main/social/logo-transparent.png" width="2%" alt="" />
  <a href="https://ultralytics.com/discord" style="text-decoration:none;">
    <img src="https://github.com/ultralytics/assets/blob/main/social/logo-social-discord.png" width="2%" alt="" /></a>
</div>

In this repository, i will using yolov5 to detect the skin disense with the input is an image and the output is a dict contain xmax, ymax, xmin, ymin, score and label of disense.

</div>
<br>

## <div align="left">Install</div>

1. Download this weight name [best.pt](https://drive.google.com/file/d/11CMf6nW1meckuQMz_mJbEzjleGuMJOWC/view?usp=drive_link) and save with the following path: public/files/weight_init/best.pt

2. Create and activate a virtual environment:

    ```sh
    $ python3 -m venv venv && source venv/bin/activate
    ```
  
3. Install the requirements:

    ```sh
    (venv)$ pip install -r requirements.txt
    ```

4. Run

    ```sh
    (venv)$ python main.py
    ```

## <div align="left">Example</div>

I wrote an example code that sends an input image, receives the output, and uses that result to draw on the input image.

Run in different console while running main.py

```python
    (venv)$ python test/test_client.py
```

{
    "content": [
        {
            "label": "Hắc lào",
            "score": "0.90",
            "xmax": 436,
            "xmin": 339,
            "ymax": 238,
            "ymin": 136
        },
        {
            "label": "Lang ben",
            "score": "0.91",
            "xmax": 306,
            "xmin": 203,
            "ymax": 169,
            "ymin": 45
        },
        {
            "label": "Hắc lào",
            "score": "0.93",
            "xmax": 537,
            "xmin": 414,
            "ymax": 213,
            "ymin": 83
        },
        {
            "label": "Lang ben",
            "score": "0.93",
            "xmax": 223,
            "xmin": 0,
            "ymax": 281,
            "ymin": 101
        },
        {
            "detected_image": "resources/images/2023/09/13/detect/17284113092023_detected.jpg",
            "original_image": "resources/images/2023/09/13/original/17284113092023_original.jpg"
        }
    ],
    "status_code": 200
}

<div align="center">
  <p>
    <img width="80%" src="./background/17281613092023_detected.jpg"></a>
    <img width="80%" src="./background/17491913092023_detected.jpg"></a>
  </p>

