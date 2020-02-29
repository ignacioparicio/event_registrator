# EventRegistrator

Weekend project of a selenium web scraper that monitors a well known sports 
website in Zurich for new community classes. When a new class becomes available, it 
emails a user and gives her the change to auto-register.

## Dependencies

All dependencies are captured in the conda env `environment.yml`. A Chrome driver 
for selenium is also required.

## Configuration
All configurable variables are contained in `config.yml`. Because it contains 
sensitive data (e.g. email password), a `config.yml.sample` is offered instead.