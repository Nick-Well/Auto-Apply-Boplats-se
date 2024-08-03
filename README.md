<h1>Working</h1>

<h2>Automaticly scrape and look for apartments on boplats</h2>
<p>
script that needs some love</br>
yea, some real love. for installation on ubuntu server you will need xorg</br>
also firefox-esr. pynput is creating alot of problems so will patch.
</p> 

<h2>Requirements:</h2>

	python3, python3-pip, selenium, BeautifulSoup4, geckodriver, webdriver_manager, pynput

<h2>Linux</h2>
<h3>Debian</h3>

	sudo apt install git python3 python3-pip
	pip install selenium BeautifulSoup4 pynput
	git clone https://github.com/Nick-Well/boplats.git

<h3>Arch</h3>

	sudo pacman -S git python python-pip
	pip install selenium BeautifulSoup4 pynput
	git clone https://github.com/Nick-Well/boplats.git

<h2>TODO:</h2>
<ul>
	<li>Docker container for ez of use</li>
	<li>Add more comments in the code</li>
	<li>Make it easyer to install. <i>barebones</i> </li>
	<li>gui?</li>
	<li>remove pynput</li>
</ul>

