# AuxFunctions
Some scripts:

  **gasmixing.py:** Control of oxygen fugacity in a Gas mixing Furnace
  
  **ebsdPlot.py:** Preview EBSD data using python (so far only EDAX '.ang' and Oxford '.ctf' files are supported). Script can be called using MAC service using Automator:
  
   Automator>New Document> Quick action(or Service)> search for 'Run Shell Script' and add it to the workflow. 
   
   Select under 'Workflow receives current': `Files or folders` 'in' `Finder`. Choose 'shell': `/bin/bash`, 'Pass input': `as arguments` and insert the following code: 
   ```bash
   /usr/bin/python2.7 /replaceHere/path/to/ebsdPlot.py "$1"
   ```
   Save the file as `Show EBSD`. The Service will be available when you click in a file with the right button>Services>Show EBSD
   
   **linearInterceptSP.m:** Linear intercept method for a single phase from EBSD data using [MTEX](https://mtex-toolbox.github.io/)
