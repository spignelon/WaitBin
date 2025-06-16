# WaitBin

WaitBin is a time-locked pastebin service that allows you to create content that remains hidden until a specific date and time. Perfect for surprises, scheduled announcements, or future messages.

🔗 **Live URL**: [https://waitbin.vercel.app/](https://waitbin.vercel.app/)

## Features

- 🔒 **Time-Locked Content**: Create pastes that remain hidden until your specified date and time arrives
- 🔗 **Shareable Links**: Get a unique link to share with anyone, showing a countdown until the content unlocks
- ✏️ **Editable Bins**: Use edit codes or create an account to manage and modify your WaitBins
- 👤 **User Accounts**: Register to easily manage all your created WaitBins in one place

## Using WaitBin

WaitBin is readily available at [https://waitbin.vercel.app/](https://waitbin.vercel.app/). Simply visit the website to start creating time-locked content right away.

## Self-Hosting

If you wish to deploy your own instance of WaitBin:

### Prerequisites

- Python 3.6+
- MongoDB

### Setup

1. Clone the repository
```bash
git clone https://github.com/spignelon/WaitBin
cd WaitBin
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following contents:
```
SECRET_KEY=your_secret_key
MONGODB_URI=mongodb://localhost:27017/
```

5. Run the application
```bash
python run.py
```

The application will be available at `http://localhost:5000`.

## Usage

1. **Creating a WaitBin**:
   - Go to the homepage and click "Create WaitBin"
   - Enter your content, title, and set the unlock date/time
   - Click "Create" to get your unique link and edit code

2. **Viewing a WaitBin**:
   - Access the link provided upon creation
   - If the unlock time has not arrived, you'll see a countdown
   - Once unlocked, the content will be revealed

3. **Editing a WaitBin**:
   - Visit the edit URL or click the edit button on your WaitBin
   - Enter your edit code (or sign in if you created it while logged in)
   - Modify the content, title, or unlock time and save changes

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS (with Tailwind CSS and DaisyUI)
- **Hosting**: Vercel

## Contributing

We welcome contributions to improve WaitBin! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch with a descriptive name (`git checkout -b feature/new-countdown-animation`)
3. Make your changes, ensuring they adhere to the project's coding style
4. Write or update tests as necessary
5. Update documentation to reflect your changes
6. Commit with clear, descriptive messages
7. Push to your fork (`git push origin feature/new-countdown-animation`)
8. Submit a Pull Request with a comprehensive description of changes

For major changes or features, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the [GPL-3.0 License](LICENSE). <br>
[![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl-3.0.en.html)
