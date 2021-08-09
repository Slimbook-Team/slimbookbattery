# Slimbookbattery
Slimbook Battery 4 is the new version with new features that improves battery control and increases battery duration in laptops.

This update offers new possibilities to the users, thanks to the integration with other applications, services and drivers like TLP, intel_pstate, AMD and NVIDIA.

This means that this application it's not only compatible with SLIMBOOK computers but with other brands and computer manufacturers that work with Ubuntu and derivatives.

The application implements three different energy modes: «energy saving», «balanced» and «maximum performance». Each energy mode comes with default values but the user is allowed to change the most important values, to adjust or avoid errors in their hardware.

The energy save applications like TLP are based on "If I i'm not using it consumes and consumes, I better turn it off". In this way the consumption of resources is reduced when the computer uses the battery. Slimbook Battery 4 uses this premise as a source of energy saving.

# Install

You can download Slimbook Battery from our application download center for Linux with our repositories in Launchpad. You can do it too if you introduce this in a Terminal (Ctrl+Alt+T):

``sudo add-apt-repository ppa:slimbook/slimbook`
sudo apt-get update``

By doing this we will have added the Slimbook repositories. Now we will execute the next command to install the application:

`sudo apt-get install slimbookbattery`

Now, you can start the application, and select a "energy profile" in the trayicon.

This app work with desktops: Unity, GNOME, KDE Plasma, Cinnamon, Mate...
