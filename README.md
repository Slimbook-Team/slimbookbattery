# Slimbookbattery

Slimbook Battery 4 is the new version with new features that improves battery control and increases battery duration in laptops.

This update offers new possibilities to the users, thanks to the integration with other applications, services and drivers like TLP, intel_pstate, AMD and NVIDIA.

This means that this application it's not only compatible with SLIMBOOK computers but with other brands and computer manufacturers that work with Ubuntu and derivatives.

The application implements three different energy modes: «energy saving», «balanced» and «maximum performance». Each energy mode comes with default values but the user is allowed to change the most important values, to adjust or avoid errors in their hardware.

The energy save applications like TLP are based on "If I i'm not using it and consumes, I better turn it off". In this way the consumption of resources is reduced when the computer uses the battery. Slimbook Battery 4 uses this premise as a source of energy saving.


![Captura de pantalla de 2021-10-01 12-58-49](https://user-images.githubusercontent.com/18195266/135992289-d05ac9eb-5c00-4525-8641-e09efee8608f.png)


# Install for testing
Download the .deb file here:
https://github.com/slimbook/slimbookbattery/releases

Run command:
  `sudo apt install ./slimbookbattery_4.0.0_all.deb`

# Install 
* ## For debian based distros
	You can download Slimbook Battery from our application download center for Linux with our repositories in Launchpad. You can do it too if you introduce this in a Terminal (Ctrl+Alt+T):

		sudo add-apt-repository ppa:slimbook/slimbook
		sudo apt update

	By doing this we will have added the Slimbook repositories. Now we will execute the next command to install the application:

		sudo apt install slimbookbattery
<br />

* ## From this repository-source   
	Donwload entire repo. Navigate to it in a terminal. And run deploy.sh script:

		./deploy.sh

	It will deploy SlimbookBattery in your system, check and install Python dependencies prepare all.
<br />

# Collaborate
You can help us by taking a look at our [**To do list**](https://github.com/slimbook/slimbookbattery/projects/1)

<br />

# Tips and frequent questions 


* ### What should I do after install?

  The first of all will be to start the main launcher of Slimbook Battery, so that the application will perform the initial configuration that applies the first time it is opened. Now you can start using any of the 3 energy saving modes and access the configuration, if you wish.

 
* ### What energy level is recommended by you?

  The level of energy we recommend would depend on the use you give to your laptop. If you are going to give an office use, that is, perform basic tasks such as surfing the Internet to visit a page, answer emails or write a document, we recommend using the Energy Saving mode. On the other hand, if you want to give it another type of use that requires more resources for certain applications, it is already recommended to use the Balanced mode or the Maximum performance mode.

 
* ### Why isn't it displayed in my language?

  Currently Slimbook Battery is only available in Spanish, English, Galician, Italian and Portuguese, so that it appears in your language you have to have the system in one of the previously mentioned languages. In case the language of the system you use is not any of the named, the application will be shown by default in English.
  If you want Slimbook Battery also to be available in your language and you want to make the translation yourself, you can consult our repository where we have uploaded the files to make the translations in any language.

* ### I do not see the Slimbook Battery indicator in the taskbar
  This may be because you have the option to disable Icon on the taskbar.

  If this is the case, you simply have to start Slimbook Battery Preferences, enable this option again and restart Slimbook Battery.
  
  > If you are using Elementary OS, then you need to install [wingpanel-indicator-ayatana](https://github.com/Lafydev/wingpanel-indicator-ayatana), follow the instructions to install it.

  In case it still does not appear, check that you have installed gnome-shell-extension-appindicator. If you don't have it installed, do it:

      sudo apt-get install gnome-shell-extension-appindicator

  Once it has been installed, restart your session, and open the preferences window, the indicator should now appear if you click the accept button. 
  

  ![imagen](https://user-images.githubusercontent.com/18195266/134377358-76eeb997-71c3-49bd-a108-4db8588544f0.png)


* ### How to uninstall Slimbook Battery

  To uninstall Slimbook Battery:

      sudo apt purge slimbookbattery

  To uninstall TLP:

      sudo apt purge tlp tlp-drw
    

* ### I have another problem or doubt about Slimbook Battery, where can I contact to solve it?

  You can contact us for anything you need regarding Slimbook Battery by sending an email to: dev@slimbook.es

  We would appreciate that you attach the file that is generated by clicking on the Generate report button of the Information tab in Slimbook Battery Preferences,  as it helps us in a great measure to continue improving Slimbook Battery.



  This app has been tested with: Unity, GNOME, KDE Plasma, Cinnamon, Pantheon...


