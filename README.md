# 🎬 Movie Recommender System

A powerful content-based movie recommendation system with dual-mode functionality: get AI-powered movie recommendations or search movies by actors and directors.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.50-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-live-success.svg)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7.svg)](https://movie-recommendor-jp89.onrender.com/)

## ✨ Features

### 🎯 Dual Search Modes

#### 1. **Recommend Similar Movies**
- Select any movie from 4,805+ titles
- Get 5-25 personalized recommendations
- Based on ML-powered cosine similarity
- Analyzes: genres, cast, crew, plot keywords

#### 2. **Search by Actor/Director**
- Type any actor or director name
- Filter by actors, directors, or both
- Partial name matching supported
- See all movies featuring that person

### 🎨 Beautiful UI
- Dark theme with purple gradients
- Responsive 4-column grid layout
- Movie posters from OMDb API
- Smooth animations and hover effects
- Professional Lucide React icons

### 📊 Rich Movie Details
- IMDb ratings (⭐ out of 10)
- Release year
- Runtime and genres
- Plot summaries
- Director and main cast
- Similarity match scores

## 🚀 Live Demo

🔗 **[https://movie-recommendor-jp89.onrender.com/](https://movie-recommendor-jp89.onrender.com/)** - Try it now!

## 📸 Screenshots

_Add screenshots of your app here_

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **ML/AI:** scikit-learn (Cosine Similarity, CountVectorizer)
- **Data Processing:** pandas, numpy, NLTK
- **API:** OMDb API for movie metadata
- **Text Processing:** Porter Stemmer for feature extraction

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip package manager
- Git LFS (for large similarity matrix file)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DeepMehta06/movie_recommendor.git
   cd movie_recommendor
   ```

2. **Install Git LFS and pull large files:**
   ```bash
   git lfs install
   git lfs pull
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   - `movies.pkl` (4,805 movies with cast/crew data)
   - `similarity_list.pkl` (4805x4805 similarity matrix)
4. **Ensure pickle files exist:**
   - `movies.pkl` (2.16 MB - movie dataset)
   - `similarity_list.pkl` (176 MB - similarity matrix, via Git LFS)

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

6. **Open browser:**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
movie_recommendor/
├── app.py                      # Main Streamlit application
├── movies.pkl                  # Preprocessed movie dataset
├── similarity_list.pkl         # Cosine similarity matrix
├── requirements.txt            # Python dependencies
├── Procfile                    # Deployment configuration
├── runtime.txt                 # Python version
├── .streamlit/
│   └── config.toml            # Streamlit settings
├── DEPLOYMENT_GUIDE.md        # Render deployment guide
└── README.md                   # This file

../
├── index_organized.ipynb       # Data preprocessing notebook
├── regenerate_pickle.py        # Script to regenerate pickle files
├── tmdb_5000_movies.csv       # Original movie dataset
└── tmdb_5000_credits.csv      # Movie credits dataset
```

## 🎯 How It Works

### Content-Based Filtering Pipeline

1. **Data Loading:** TMDb 5000 dataset (movies + credits)
2. **Feature Extraction:**
   - Genres, keywords, plot overview
   - Top 3 cast members
   - Director information
3. **Text Processing:**
   - Combine features into single "tag"
   - Apply Porter Stemming
   - Remove stop words
4. **Vectorization:**
   - CountVectorizer (5000 features)
   - Convert text to numerical vectors
5. **Similarity Computation:**
   - Cosine similarity between all movie vectors
   - 4805×4805 similarity matrix
6. **Recommendation:**
   - Find movies with highest similarity scores
   - Return top K recommendations

### Actor/Director Search

1. **Normalize Input:** Remove spaces, lowercase
2. **Search Cast Column:** Match against actor names
3. **Search Crew Column:** Match against director names
4. **Return Results:** All movies featuring the person

## 🔑 API Configuration

Get your free OMDb API key:
1. Visit [omdbapi.com](http://www.omdbapi.com/apikey.aspx)
2. Sign up for free tier (1,000 requests/day)
3. Update `OMDB_API_KEY` in `app.py` (line 95)

```python
OMDB_API_KEY = "your_api_key_here"
```

## 🌐 Deployment

✅ **Currently deployed on [Render](https://render.com/)** - Live at [movie-recommendor-jp89.onrender.com](https://movie-recommendor-jp89.onrender.com/)

### Deploy Your Own Instance

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Create Render Web Service:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Settings:**
   - **Name:** movie-recommendor (or your choice)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh`
   - **Environment Variable:** `PYTHON_VERSION` = `3.11.0`

4. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Your app will be live!

**Note:** Free tier on Render includes:
- 512 MB RAM
- Automatic deploys from GitHub
- Custom domain support
- HTTPS included

## 📊 Dataset Information

- **Source:** TMDb 5000 Movie Dataset
- **Movies:** 4,805 entries
- **Features:** 
  - Title, ID, overview
  - Genres, keywords
  - Cast (top 3 actors)
  - Crew (directors)
  - Release date, runtime
- **Time Period:** Various (classic to modern movies)

## 🎨 UI Features

- **Material Design Icons:** Clean, professional look
- **Lucide React Icons:** SVG icons for badges
- **Responsive Grid:** Adapts to screen size
- **Popover Details:** Non-intrusive info display
- **Progress Bars:** Visual similarity scores
- **Smooth Animations:** Hover effects and transitions

## 🔧 Configuration

### Adjust Recommendations
In sidebar, use the slider:
- Min: 5 movies
- Max: 25 movies
- Default: 20 movies

### Modify Search Filters
Actor/Director search options:
- Both (default)
- Actors only
- Directors only

## 🐛 Troubleshooting

### Images Not Loading
- Check OMDb API key validity
- Verify internet connection
- Some movies may not have posters

### Pickle Files Missing
```bash
cd ..
python regenerate_pickle.py
```

### Module Not Found
```bash
pip install -r requirements.txt
```

## 📈 Performance

- **Load Time:** ~2-3 seconds
- **Recommendation Speed:** <1 second
- **Search Speed:** <2 seconds
- **API Calls:** Cached for 1 hour
- **Memory Usage:** ~150MB (with pickle files)

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Deep Mehta**
- GitHub: [@DeepMehta06](https://github.com/DeepMehta06)

## 🙏 Acknowledgments

- TMDb for the movie dataset
- OMDb API for movie metadata
- Streamlit for the amazing framework
- Lucide for beautiful icons

## 📞 Support

Having issues? 
- Check [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Open an issue on GitHub
- Contact: [Your Email]

---

⭐ **Star this repo if you found it helpful!**
