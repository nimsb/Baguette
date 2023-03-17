Baguette is a drag, drop and connect system rig. Each item you create is a module which carries all the data of that item.
The goal of this system is to provide the ability to easily develop rigs by any riggers from all level. 

The python compiled code version(.pyd files) here is for Maya 2023 on windows. the python files (.py),  and qt (.ui) files works for any version. 
Please check the released version to have access to other Maya compiled code (2019, 2020 and 2022)

INSTALL
- go to the release page : https://github.com/nimsb/Baguette/releases
- VERY IMPORTANT : download the version according to your Maya version 
- unzip the Baguette folder into your Maya script folder. You should have something like this

![alt text](https://i.ibb.co/MCzKpx1/image.png)

To launch Baguette UI:
```
from Baguette import reload_package
reload_package()
````

To use some of the rigUtils : 
```
from Baguette.utils import rigUtils

#copy skinning
rigUtils.copySkin(source, sel)

#mirror some shape
rigUtils.mirrorShape()
``` 
TO DO : a more extensive documentation will come.
