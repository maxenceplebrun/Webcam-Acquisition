<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!--  [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a >
    <img src="assets/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Webcam Acquisition</h3>

  <p align="center">
    A Python GUI designed to acquire webcam images synchronised with a widefield imaging system. 
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
<div align="center">
  <a >
    <img src="assets/screenshot.png" alt="Logo" width="700">
  </a>
</div>

There are many Widefield Imaging programs available on the Internet. However, they tend to be unnecessarily complex to use or limited in their capacities. With the present software, we hope to achieve a balance between usability and feature-richness, allowing simple acquisitions as well as complex workflows. Some of the main features of the program are:
* The ability to acquire laser speckle, fluorescence and intrinsic optical imaging at the same time
* The recursive stimulation generation tools, including different signal shapes and support for delay, jitter and repeat
* The support for multiple stimulation channels and their visual rendering
* The visual display of live video channels and activations maps
* ...And much more!

You can download the program by following the instructions below. Some indications are also given on how to adapt the program to your current setup. Note that **only National Instruments DAQs and IMAQ-compatible cameras have built-in support**. If you want to use other devices, you will need to so some coding on your own.
<p align="right">(<a href="#top">back to top</a>)</p>



### Built With


* [Python](https://www.python.org/)
* [PyQt5](https://riverbankcomputing.com/software/pyqt/)
* [OpenCV](https://opencv.org/)
* [Numpy](https://numpy.org/)



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
- Python 3.9 must be installed

### Installation
1. Download the latest release in the [Releases](https://github.com/midesjardins/Widefield-Imaging-Acquisition/releases) section of the repository.
2. Unzip the downloaded file and move to desired location.
3. Install the required modules using one of the following methods:

#### Using Pip
1. Open a terminal window
2. Go to the directory where the program is saved using the `cd` command.
2. Run the following command: ```pip install -r requirements.txt```

### Using Anaconda
1. Open a terminal window
2. Run the following two commands:
```
conda create -n py3.9 python=3.9.12
conda activate py3.9
```
3. In a terminal window, go to the directory where the program is saved using the `cd` command.
4. Run the following command:
```pip install -r requirements.txt```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Running the program
1. Launch the `webcam.pyw` module found in the `gui` subfolder.

### Modifying the Arduino COM port
1. Open the ```config.json``` file using any text editor.
2. Replace the string at te ```arduino_port``` key with the desired port.

### Modifying the Arduino input PIN
1. Open the ```arduino.ino``` file using any text editor.
2. On the first line, replace the `inPin` variable with the desired PIN port number.
3. Transfer the `arduino.ino` file to the board using the Arduino Software. 

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/midesjardins/Widefield-Imaging-Acquisition/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>





<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Created by Maxence Pelletier-Lebrun - maxencepelletierlebrun@gmail.com

For a research internship at Michèle Desjardins' Laboratory 

Research Page: [https://www.crchudequebec.ulaval.ca/recherche/chercheurs/michele-desjardins/](https://www.crchudequebec.ulaval.ca/recherche/chercheurs/michele-desjardins/)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png