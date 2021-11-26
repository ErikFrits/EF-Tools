# 🛠 EF-Tools 🛠 
![EF-Tools](https://github.com/ErikFrits/EF-Tools/blob/main/EF-Tools%20Overview.PNG?raw=true)

EF-Tools is a custom extension for pyRevit that contains multiple tools that might help you.  
Developed by **Erik Frits**




### 📦 Revit Versions 📦
These tools were developed mainly in Revit 2021.  
In case you are using different version of Revit and having any issues,  
please let me know so I could adjust them to work on other versions too.

##  🎉 Release v1.0 🎉
I have contacted the creator of pyRevit - Ehsan Iran-Nejad, and he said that he will 
add my extension to pyRevit extensions with its next release by default.

You are welcome to use them right now but you will need to modify `extensions.json` file in `pyRevit-Master` manually.
Follow installation instructions below.

#### 💠 Installation 💠 

#### 🎬 YouTube Tutorial - https://www.youtube.com/watch?v=q0zbdyyBIo0
1) Find `extensions.json` file that is normally saved in the path below by default:  
`%appdata%\pyRevit-Master\extensions` or sometimes it can be found here `C:\Program Files\pyRevit-Master`
2) Open `extension.json` file in `pyRevit-Master\extensions\`. Once you open this .json file 
you will see a dictionary of other extensions. We will need to manually add information about EF-Tools here
3) Open [`extension.json`](https://github.com/ErikFrits/EF-Tools/blob/main/extension.json) file in my repo.
4) Add the content of my file to the `%appdata%\pyRevit-Master\extensions\extensions.json` so it 
matches the other extensions listed in there. Or just replace the file's content with [`extension.json`](https://github.com/ErikFrits/EF-Tools/blob/main/installation/extension.json)

Contact me if you need help installing it.

### 📜 List of tools 📜

- [x] Sheets
    - [x] Sheets: Add specific revision
    - [x] Sheets: Create multiple
    - [x] Place views on new sheets
    - [x] Sheets: Duplicate
    - [x] Sheets: Revision History
    
- [ ] Attached Groups
    - [ ] Attached groups: Show on selected Views
    - [ ] Attached groups: Duplicate 
        
- [x] Views
    - [x] Duplicate views
    - [x] Group/Hide revision clouds (WIP)
    - [x] Create Workset 3D Views
    
- [ ] Maintenance
    - [ ] Purge: LinePatterns
    - [ ] Purge: ViewFilters
    - [ ] Warnings: Enable leader
    - [ ] Warnings: Does not intersect
    
- [x] Elements
    - [x] Elements: Rotate
    - [x] Regions: Change LineStyle
    - [x] Wall Match: Top Constraints
    - [x] Wall Match: Both Constraints
    - [x] Wall Match: Bottom Constraints
    
- [x] Selection
    - [x] Super select in view (SS)
    - [x] Super select in model (SA)
    - [x] Selection
        - [x] Select Title Blocks on sheets
        - [x] Select DWG on sheets
        - [x] Select similar categories (in model)
        - [x] Select similar categories (in view)
        - [ ] Select elements of selected groups

- [x] Naming
    - [x] Rename
        - [x] Find and Replace: Views
        - [x] Find and Replace: Sheets
        - [x] Find and Replace: RoomNames
        - [x] Find and Replace: Types
    - [x] Text: Transform
    
- [x] UI
    - [x] B/W/G 
    - [x] List all levels
    - [x] Shorten Ribbon names
           
- [ ] Rooms
    - [x] Rooms to Floors
    - [x] Rooms to Regions
    - [ ] Rooms SUM* (might be too office specific)
    
- [ ] DWG
    - [x] Open selected DWG
    - [x] Save/Relink all DWGs
    - [ ] Save/Relink all JPGs
        
- [ ] Other Upcoming Tools 
    - [ ] Sheets: Allign viewports
    - [ ] Purge: all areas
    - [ ] Rooms: Flat Renumbering
    - [ ] Rename DWGs
    - [ ] Naming: Wall/Roof/Floor Types 
    - [ ] Delete 0 dimensions
    - [ ] Parking: Renumber with spline
    - [ ] Apartments groups: Renumber with spline 


### [🌐 My personal blog 🌐](www.erikfrits.com/blog "Erik Frits - Blog") 
My website is still in development and I am lacking time, so please do not expect much from it right now.

I will be sharing different snippets and explaining some of my scripts on my blog. 
Hopefully some of you will learn something from me.

## Contact me
🤵 https://www.linkedin.com/in/erik-frits  
📨 erikfrits95@gmail.com

