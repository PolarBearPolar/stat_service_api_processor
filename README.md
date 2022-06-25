# stat_service_api_processor
There is a great statistical service called OECD. As for me, its API is quite sophisticated and can be used as a good example of how APIs can be processed to transform data to different human-readable formats.

Here is my project that uses Python and Docker to transform OECD datasets to flat tables. The program is run in a container so that you do not need to worry about dependencies.

In order to use the program, you should follow the steps below:
- Clone the repo
- Run the following Docker command to build an image **docker build --tag oecd_dataset_processor:0.1 <path_to_oecd_dataset_processor_directory>**
- There is an example **oecd_dataset_processor.bat** file to run a container from an executable script. The content of this file is below.

![image](https://user-images.githubusercontent.com/88388315/175759620-ecf4854a-f89e-4304-88ec-225a26f278f1.png)

  - You can replace lines 2,3,4 with whatever options you like. Available save modes are **xlsx**, **txt** (txt is more preferable for large datasets). 
  - The xml file that contains available datasets can be found on https://stats.oecd.org/restsdmx/sdmx.ashx/GetDataStructure/all. Dataset identifiers are in elements that have the **KeyFamily** tag. The identifiers are the values of id attributes.

I hope you will like it 🙂
