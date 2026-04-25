# 🎈 Eclipse Mission Control

**Track weather balloons in real-time. See the Earth from 35,000 meters up. Control your own high-altitude mission. No experience needed.**

---

## 🚀 What Is This?

Imagine launching a weather balloon that climbs higher than airplanes fly. As it rises, it sends back:
- 📍 **Live location** - where it is right now
- 🌡️ **Temperature readings** - it gets colder the higher it goes
- 📸 **Photos from space** - actual pictures from the balloon's camera
- 🔋 **Battery status** - is it still working?

**Eclipse Mission Control** is the command center that collects all this data and shows it to you on a beautiful dashboard. You can see:
- 🗺️ **Interactive maps** showing the balloon's flight path
- 📊 **Live charts** tracking altitude, temperature, and more
- 👥 **Your entire balloon fleet** in one place
- 🎥 **Photos** captured as it rises through the atmosphere

It's like being a NASA mission controller, but for weather balloons! 🌍

---

## ✨ Cool Features

### 🎯 Real-Time Tracking
Watch your balloons climb in real-time. See exactly where they are on a map, refreshing every 30 seconds.

### 📈 Beautiful Data Visualization
Altitude charts, temperature graphs, and more. Beautiful enough to put on your science fair project.

### 🎮 Simple to Start
- **No expert knowledge required** - we include sample data so you can see it working immediately
- **Easy setup** - just a few commands to get running
- **Instant gratification** - launch a simulation and watch it go

### 📱 Works Everywhere
Built with modern web tech that works on phones, tablets, laptops - whatever you have.

### 🔌 API Ready
Send data from any device. Whether you build a real balloon or just want to test with data, our API accepts your numbers.

---

## 🎬 Quick Start (5 Minutes)

### 1. **Get the Code**
```bash
git clone https://github.com/james-bi/eclipse-mission-control.git
cd eclipse-mission-control
```

### 2. **Install**
```bash
pip install -r requirements.txt
python manage.py migrate
```

### 3. **Launch Demo**
```bash
# Create sample balloons with fake data
python manage.py generate_mock_data

# Start the server
python manage.py runserver
```

### 4. **See It Live**
Open your web browser to **`http://localhost:8000`**

That's it! You'll see a dashboard with sample balloons and live telemetry data. 🎉

---

## 🎮 Try a Simulation

Want to see the balloons actually flying? Run a simulation:

```bash
# Simulate one balloon
python manage.py simulate_flight --balloon-id scout-123 --interval 5

# Or simulate ALL balloons to see the fleet in action
python manage.py simulate_flight
```

Watch the dashboard as the balloons climb! Altitude increases, temperature drops, batteries drain - it's realistic physics. 🌡️↓

---

## 🏗️ How Does It Work?

```
Real Weather Balloon     Dashboard (Your Computer)     Database
         ↓                         ↓                        ↓
    Sends Data     →    Mission Control Receives    →   Stores History
    (Location,          (Shows on Beautiful          (Remembers
     Altitude,          Dashboard with Charts)        Everything)
     Temp, Photos)
```

**In boring tech terms:** It's a Django web app with a REST API. Balloons (or simulators) send JSON data to the API, which stores it in a database. The dashboard reads that data and displays it beautifully. But you don't need to understand that to use it! 😄

---

## 💡 What Can You Do With This?

### 🎓 **For School Projects**
- Science fair winner - real data, beautiful visualization
- Learn how tracking systems work
- Understand high-altitude weather patterns
- Computer science credit - bonus points!

### 🏕️ **For Scout Camps**
- Fly balloons with your troop
- Track them live
- Share data with friends
- Official mission control room vibes 🎉

### 👨‍💻 **For Learning to Code**
- See a full web app in action
- Understand databases and APIs
- Learn how frontend and backend talk to each other
- Free project to modify and experiment with

### 🔬 **For Personal Experiments**
- Send data from your own sensors
- Track anything that can send GPS coordinates
- Build your own "space mission"

---

## 📊 Example: Your Balloon's Data

The dashboard shows you everything your balloon sends:

```
🎈 Scout Troop 123 Balloon
━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Latitude:     40.7128°
📍 Longitude:    -74.0060°
📏 Altitude:     12,400 m (higher than planes!)
🌡️  Temperature:  -35.2°C (freezing!)
🔋 Battery:      78%
🕐 Last Update:   Just now
```

All tracked on a live map with historical charts. 📈

---

## 🤔 Questions?

### "Do I need experience to use this?"
**No!** Just follow the Quick Start above. We've designed it to work right out of the box.

### "Can I modify it?"
**Yes!** It's fully open source. Change colors, add features, break things and learn. That's how coding works! 🎨

### "Can I use real balloon data?"
**Absolutely!** Our API accepts any data. Send it from a real balloon, a simulator, or a sensor. Here's how: see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

### "What if I get stuck?"
Check out [SIMULATION_GUIDE.md](SIMULATION_GUIDE.md) for detailed setup instructions and troubleshooting.

---

## 🛠️ Tech Stack (You Don't Need to Know This)

- **Backend:** Django (Python web framework)
- **Database:** MySQL (stores all the data)
- **Frontend:** HTML, CSS, JavaScript (what you see in the browser)
- **Charting:** Chart.js (those pretty graphs)
- **Maps:** Google Maps API (the interactive map)
- **Extras:** HTMX, Tailwind CSS (makes it fancy)

**Translation:** It's a modern web app that works super fast and looks awesome. 🚀

---

## 📚 Next Steps

1. ✅ Run the Quick Start above
2. 📖 Explore the dashboard - click around!
3. 🎮 Try the simulation to see balloons fly
4. 📋 Check [SIMULATION_GUIDE.md](SIMULATION_GUIDE.md) for more advanced stuff
5. 🔌 Read [API_DOCUMENTATION.md](API_DOCUMENTATION.md) if you want to send real data
6. 🎨 Customize colors, add features, make it yours!

---

## 💬 Join Us!

Got ideas? Found a bug? Want to add features?

- 🌟 Star this repo if you think it's cool
- 🐛 Tell us about issues
- 🔄 Submit improvements (pull requests)
- 💕 Spread the word to other makers

---

## 📜 License

MIT License - Use it, modify it, share it. Just keep the license header. See [LICENSE](LICENSE) for details.

---

**Happy tracking! 🎈📡** 

*Built with ❤️ for everyone who's ever wondered what the sky looks like from 35,000 meters up.*