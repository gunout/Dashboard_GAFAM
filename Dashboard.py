# dashboard_gafam_live.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import warnings
import yfinance as yf

warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard GAFAM - Temps Réel",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avec animations temps réel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #4285F4, #34A853, #FBBC05, #EA4335, #8A2BE2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #FF0000, #FF6B6B);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    .real-time-flash {
        animation: flash 0.5s;
    }
    @keyframes flash {
        0% { background-color: transparent; }
        50% { background-color: #ffff99; }
        100% { background-color: transparent; }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4285F4;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .section-header {
        color: #4285F4;
        border-bottom: 2px solid #EA4335;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .stock-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #4285F4;
        background-color: #f8f9fa;
        transition: all 0.3s ease;
    }
    .stock-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .price-change {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .positive { 
        background-color: #d4edda; 
        border-left: 4px solid #28a745; 
        color: #155724; 
    }
    .negative { 
        background-color: #f8d7da; 
        border-left: 4px solid #dc3545; 
        color: #721c24; 
    }
    .neutral { 
        background-color: #e2e3e5; 
        border-left: 4px solid #6c757d; 
        color: #383d41; 
    }
    .sector-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .ticker-tape {
        background: linear-gradient(90deg, #4285F4, #34A853, #FBBC05, #EA4335);
        color: white;
        padding: 10px 0;
        overflow: hidden;
        white-space: nowrap;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .ticker-content {
        display: inline-block;
        padding-left: 100%;
        animation: ticker 30s linear infinite;
    }
    @keyframes ticker {
        0% { transform: translateX(0); }
        100% { transform: translateX(-100%); }
    }
</style>
""", unsafe_allow_html=True)

class RealTimeGAFAMDashboard:
    def __init__(self):
        self.entreprises = self.define_entreprises()
        self.historical_data = {}
        self.last_update = datetime.now()
        self.update_frequency = 10  # secondes
        self.real_time_prices = {}  # CORRECTION: Déplacé avant initialize_current_data() pour éviter l'AttributeError
        
        # Initialiser les données historiques
        self.initialize_historical_data()
        
        # Initialiser les données courantes après avoir initialisé real_time_prices
        self.current_data = self.initialize_current_data()
        
    def define_entreprises(self):
        """Définit les entreprises du GAFAM avec leurs tickers"""
        return {
            'GOOGL': {
                'nom_complet': 'Alphabet Inc. (Google)',
                'secteur': 'Technologie',
                'sous_secteur': 'Recherche Internet & Publicité',
                'pays': 'USA',
                'couleur': '#4285F4',
                'poids_gafam': 20.0,
                'description': 'Leader mondial de la recherche internet et publicité digitale',
                'fondation': 1998,
                'fondateurs': 'Larry Page, Sergey Brin'
            },
            'AAPL': {
                'nom_complet': 'Apple Inc.',
                'secteur': 'Technologie',
                'sous_secteur': 'Électronique & Logiciels',
                'pays': 'USA',
                'couleur': '#A2AAAD',
                'poids_gafam': 25.0,
                'description': 'Leader mondial des technologies et électronique grand public',
                'fondation': 1976,
                'fondateurs': 'Steve Jobs, Steve Wozniak, Ronald Wayne'
            },
            'META': {
                'nom_complet': 'Meta Platforms Inc.',
                'secteur': 'Technologie',
                'sous_secteur': 'Réseaux Sociaux & Métaverse',
                'pays': 'USA',
                'couleur': '#1877F2',
                'poids_gafam': 15.0,
                'description': 'Leader des réseaux sociaux et plateformes de connexion',
                'fondation': 2004,
                'fondateurs': 'Mark Zuckerberg'
            },
            'AMZN': {
                'nom_complet': 'Amazon.com Inc.',
                'secteur': 'Technologie',
                'sous_secteur': 'E-commerce & Cloud Computing',
                'pays': 'USA',
                'couleur': '#FF9900',
                'poids_gafam': 22.0,
                'description': 'Leader mondial du e-commerce et des services cloud',
                'fondation': 1994,
                'fondateurs': 'Jeff Bezos'
            },
            'MSFT': {
                'nom_complet': 'Microsoft Corporation',
                'secteur': 'Technologie',
                'sous_secteur': 'Logiciels & Cloud Computing',
                'pays': 'USA',
                'couleur': '#7FBA00',
                'poids_gafam': 18.0,
                'description': 'Leader mondial des logiciels et solutions cloud',
                'fondation': 1975,
                'fondateurs': 'Bill Gates, Paul Allen'
            },
            'NFLX': {
                'nom_complet': 'Netflix Inc.',
                'secteur': 'Divertissement',
                'sous_secteur': 'Streaming Vidéo',
                'pays': 'USA',
                'couleur': '#E50914',
                'poids_gafam': 8.0,
                'description': 'Leader mondial du streaming vidéo',
                'fondation': 1997,
                'fondateurs': 'Reed Hastings, Marc Randolph'
            },
            'TSLA': {
                'nom_complet': 'Tesla Inc.',
                'secteur': 'Automobile',
                'sous_secteur': 'Véhicules Électriques & Énergie',
                'pays': 'USA',
                'couleur': '#E82127',
                'poids_gafam': 12.0,
                'description': 'Leader des véhicules électriques et énergies renouvelables',
                'fondation': 2003,
                'fondateurs': 'Martin Eberhard, Marc Tarpenning'
            }
        }
    
    def get_real_time_price(self, symbol):
        """Récupère le prix en temps réel via Yahoo Finance"""
        try:
            # Utiliser yfinance pour les données temps réel
            stock = yf.Ticker(symbol)
            data = stock.history(period='1d', interval='1m')
            
            if not data.empty:
                latest = data.iloc[-1]
                return {
                    'prix': latest['Close'],
                    'volume': latest['Volume'],
                    'timestamp': datetime.now(),
                    'variation': latest['Close'] - data['Open'].iloc[0] if len(data) > 0 else 0,
                    'variation_pct': ((latest['Close'] - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100 if len(data) > 0 else 0
                }
            else:
                # Fallback: données quotidiennes
                data = stock.history(period='1d')
                if not data.empty:
                    latest = data.iloc[-1]
                    return {
                        'prix': latest['Close'],
                        'volume': latest['Volume'],
                        'timestamp': datetime.now(),
                        'variation': latest['Close'] - latest['Open'],
                        'variation_pct': ((latest['Close'] - latest['Open']) / latest['Open']) * 100
                    }
        except Exception as e:
            st.error(f"Erreur données temps réel {symbol}: {e}")
        
        return None
    
    def initialize_current_data(self):
        """Initialise les données courantes en temps réel"""
        current_data = []
        
        for ticker, info in self.entreprises.items():
            real_time_data = self.get_real_time_price(ticker)
            
            if real_time_data:
                current_data.append({
                    'symbole': ticker,
                    'nom_complet': info['nom_complet'],
                    'secteur': info['secteur'],
                    'prix_actuel': real_time_data['prix'],
                    'variation_pct': real_time_data['variation_pct'],
                    'variation_abs': real_time_data['variation'],
                    'volume': real_time_data['volume'],
                    'timestamp': real_time_data['timestamp'],
                    'poids_gafam': info['poids_gafam'],
                    'fondation': info['fondation'],
                    'fondateurs': info['fondateurs'],
                    'dernier_prix': real_time_data['prix']  # Pour comparaison
                })
                
                # Stocker le prix pour le ticker tape
                self.real_time_prices[ticker] = real_time_data['prix']
        
        return pd.DataFrame(current_data)
    
    def initialize_historical_data(self):
        """Initialise les données historiques pour chaque entreprise"""
        for ticker in self.entreprises.keys():
            try:
                stock = yf.Ticker(ticker)
                # Récupérer les données des 7 derniers jours avec un intervalle de 5 minutes
                hist = stock.history(period='7d', interval='5m')
                self.historical_data[ticker] = hist
            except Exception as e:
                st.error(f"Erreur historique {ticker}: {e}")
    
    def update_live_data(self):
        """Met à jour les données en temps réel"""
        try:
            new_data = []
            
            for ticker, info in self.entreprises.items():
                real_time_data = self.get_real_time_price(ticker)
                
                if real_time_data:
                    # Vérifier si le prix a changé pour l'animation
                    old_price = self.real_time_prices.get(ticker, 0)
                    new_price = real_time_data['prix']
                    
                    new_data.append({
                        'symbole': ticker,
                        'nom_complet': info['nom_complet'],
                        'secteur': info['secteur'],
                        'prix_actuel': new_price,
                        'variation_pct': real_time_data['variation_pct'],
                        'variation_abs': real_time_data['variation'],
                        'volume': real_time_data['volume'],
                        'timestamp': real_time_data['timestamp'],
                        'poids_gafam': info['poids_gafam'],
                        'fondation': info['fondation'],
                        'fondateurs': info['fondateurs'],
                        'dernier_prix': old_price,
                        'prix_change': new_price != old_price
                    })
                    
                    # Mettre à jour le prix réel
                    self.real_time_prices[ticker] = new_price
            
            if new_data:
                self.current_data = pd.DataFrame(new_data)
                self.last_update = datetime.now()
                
        except Exception as e:
            st.error(f"Erreur mise à jour temps réel: {e}")
    
    def display_ticker_tape(self):
        """Affiche le bandeau défilant avec les prix en temps réel"""
        if self.current_data.empty:
            return
            
        ticker_items = []
        for _, row in self.current_data.iterrows():
            change_class = "positive" if row['variation_pct'] > 0 else "negative" if row['variation_pct'] < 0 else "neutral"
            arrow = "▲" if row['variation_pct'] > 0 else "▼" if row['variation_pct'] < 0 else "●"
            
            ticker_items.append(
                f"{row['symbole']}: ${row['prix_actuel']:.2f} {arrow} {row['variation_pct']:+.2f}%"
            )
        
        ticker_content = " • ".join(ticker_items)
        
        st.markdown(f"""
        <div class="ticker-tape">
            <div class="ticker-content">
                <strong>🔴 LIVE • {ticker_content} • </strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🚀 Dashboard GAFAM - TEMPS RÉEL</h1>', 
                   unsafe_allow_html=True)
        
        # Bandeau défilant
        self.display_ticker_tape()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 DONNÉES LIVE • MISE À JOUR AUTOMATIQUE</div>', 
                       unsafe_allow_html=True)
            st.markdown("**Surveillance en temps réel des géants technologiques**")
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés en temps réel"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        if self.current_data.empty:
            st.warning("Chargement des données en cours...")
            return
        
        # Calcul des métriques
        nasdaq_value = self.get_nasdaq_value()
        variation_moyenne = self.current_data['variation_pct'].mean()
        volume_total = self.current_data['volume'].sum()
        entreprises_hausse = len(self.current_data[self.current_data['variation_pct'] > 0])
        capitalisation_totale = sum([self.get_market_cap(symbol) for symbol in self.entreprises.keys()]) / 1e12
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_color = "normal" if variation_moyenne >= 0 else "inverse"
            st.metric(
                "NASDAQ Composite",
                f"{nasdaq_value:,.0f}",
                f"{variation_moyenne:+.2f}%",
                delta_color=delta_color
            )
        
        with col2:
            st.metric(
                "Entreprises en Hausse",
                f"{entreprises_hausse}/{len(self.current_data)}",
                f"{entreprises_hausse - (len(self.current_data) - entreprises_hausse):+d}",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Volume Total",
                f"{volume_total:,.0f}",
                "LIVE"
            )
        
        with col4:
            st.metric(
                "Capitalisation Totale",
                f"{capitalisation_totale:.2f} T$",
                "LIVE"
            )
    
    def get_nasdaq_value(self):
        """Récupère la valeur actuelle du NASDAQ"""
        try:
            nasdaq = yf.Ticker("^IXIC")
            hist = nasdaq.history(period='1d', interval='1m')
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except:
            pass
        return 15000  # Valeur par défaut
    
    def get_market_cap(self, symbol):
        """Estime la capitalisation boursière"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return info.get('marketCap', self.current_data[self.current_data['symbole'] == symbol]['prix_actuel'].iloc[0] * 1e9)
        except:
            if not self.current_data.empty:
                return self.current_data[self.current_data['symbole'] == symbol]['prix_actuel'].iloc[0] * 1e9
            return 1e9  # Valeur par défaut
    
    def create_real_time_charts(self):
        """Crée les graphiques en temps réel"""
        st.markdown('<h3 class="section-header">📈 GRAPHIQUES TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Prix Live", "Volume Live", "Analyse Technique"])
        
        with tab1:
            # Graphique des prix en temps réel
            fig = go.Figure()
            
            for ticker in self.entreprises.keys():
                if ticker in self.historical_data and not self.historical_data[ticker].empty:
                    hist_data = self.historical_data[ticker]
                    # Prendre seulement les 100 derniers points pour la lisibilité
                    recent_data = hist_data.tail(100)
                    fig.add_trace(go.Scatter(
                        x=recent_data.index,
                        y=recent_data['Close'],
                        name=ticker,
                        line=dict(color=self.entreprises[ticker]['couleur'], width=2)
                    ))
            
            fig.update_layout(
                title='Évolution des Prix (7 derniers jours)',
                xaxis_title='Date/Heure',
                yaxis_title='Prix ($)',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Graphique des volumes en temps réel
            fig = go.Figure()
            
            for ticker in self.entreprises.keys():
                if ticker in self.historical_data and not self.historical_data[ticker].empty:
                    hist_data = self.historical_data[ticker]
                    recent_data = hist_data.tail(100)
                    fig.add_trace(go.Bar(
                        x=recent_data.index,
                        y=recent_data['Volume'],
                        name=ticker,
                        marker_color=self.entreprises[ticker]['couleur'],
                        opacity=0.7
                    ))
            
            fig.update_layout(
                title='Volume des Transactions (7 derniers jours)',
                xaxis_title='Date/Heure',
                yaxis_title='Volume',
                height=400,
                showlegend=True,
                barmode='stack'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Analyse technique temps réel
            selected_stock = st.selectbox(
                "Sélectionnez une action:",
                list(self.entreprises.keys()),
                format_func=lambda x: f"{x} - {self.entreprises[x]['nom_complet']}"
            )
            
            if selected_stock and selected_stock in self.historical_data:
                data = self.historical_data[selected_stock]
                
                if not data.empty:
                    # Calcul des indicateurs techniques
                    data['MA20'] = data['Close'].rolling(window=20).mean()
                    data['MA50'] = data['Close'].rolling(window=50).mean()
                    data['RSI'] = self.calculate_rsi(data['Close'])
                    
                    fig = make_subplots(
                        rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=('Prix et Moyennes Mobiles', 'RSI', 'Volume'),
                        row_heights=[0.5, 0.25, 0.25]
                    )
                    
                    # Prendre les 200 derniers points pour la performance
                    recent_data = data.tail(200)
                    
                    # Prix et moyennes mobiles
                    fig.add_trace(go.Scatter(x=recent_data.index, y=recent_data['Close'], name='Prix', 
                                           line=dict(color='#4285F4')), row=1, col=1)
                    fig.add_trace(go.Scatter(x=recent_data.index, y=recent_data['MA20'], name='MM20', 
                                           line=dict(color='orange')), row=1, col=1)
                    fig.add_trace(go.Scatter(x=recent_data.index, y=recent_data['MA50'], name='MM50', 
                                           line=dict(color='red')), row=1, col=1)
                    
                    # RSI
                    fig.add_trace(go.Scatter(x=recent_data.index, y=recent_data['RSI'], name='RSI', 
                                           line=dict(color='purple')), row=2, col=1)
                    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                    
                    # Volume
                    fig.add_trace(go.Bar(x=recent_data.index, y=recent_data['Volume'], name='Volume',
                                       marker_color='lightblue'), row=3, col=1)
                    
                    fig.update_layout(height=600, title_text=f"Analyse Technique - {selected_stock}")
                    st.plotly_chart(fig, use_container_width=True)
    
    def calculate_rsi(self, prices, window=14):
        """Calcule le RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def create_real_time_table(self):
        """Crée le tableau des prix en temps réel"""
        st.markdown('<h3 class="section-header">🏢 TABLEAU DES PRIX TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        if self.current_data.empty:
            st.warning("Chargement des données en cours...")
            return False
        
        # Tri et filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_by = st.selectbox("Trier par:", 
                                 ['Variation %', 'Prix', 'Volume', 'Capitalisation'])
        with col2:
            filter_sector = st.selectbox("Filtrer secteur:", 
                                       ['Tous'] + list(self.current_data['secteur'].unique()))
        with col3:
            auto_refresh = st.checkbox("🔄 Auto-rafraîchissement", value=True)
        
        # Appliquer les filtres
        display_data = self.current_data.copy()
        if filter_sector != 'Tous':
            display_data = display_data[display_data['secteur'] == filter_sector]
        
        # Appliquer le tri
        if sort_by == 'Variation %':
            display_data = display_data.sort_values('variation_pct', ascending=False)
        elif sort_by == 'Prix':
            display_data = display_data.sort_values('prix_actuel', ascending=False)
        elif sort_by == 'Volume':
            display_data = display_data.sort_values('volume', ascending=False)
        
        # Afficher les données avec animations
        for _, row in display_data.iterrows():
            # Déterminer la classe CSS pour la variation
            change_class = ""
            if row['variation_pct'] > 0:
                change_class = "positive"
            elif row['variation_pct'] < 0:
                change_class = "negative"
            else:
                change_class = "neutral"
            
            # Vérifier si le prix a changé pour l'animation
            price_changed = row.get('prix_change', False)
            flash_class = "real-time-flash" if price_changed else ""
            
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{row['symbole']}**")
                st.markdown(f"*{row['secteur']}*")
            
            with col2:
                st.markdown(f"**{row['nom_complet']}**")
                market_cap = self.get_market_cap(row['symbole']) / 1e9
                st.markdown(f"Market Cap: {market_cap:.1f} B$")
            
            with col3:
                st.markdown(f"<div class='{flash_class}'>**${row['prix_actuel']:.2f}**</div>", 
                           unsafe_allow_html=True)
                st.markdown(f"Volume: {row['volume']:,.0f}")
            
            with col4:
                variation_str = f"{row['variation_pct']:+.2f}%"
                st.markdown(f"**{variation_str}**")
                st.markdown(f"${row['variation_abs']:+.2f}")
            
            with col5:
                st.markdown(f"<div class='price-change {change_class} {flash_class}'>{variation_str}</div>", 
                           unsafe_allow_html=True)
            
            with col6:
                # Indicateur de tendance
                if row['variation_pct'] > 1:
                    st.markdown("📈 Forte hausse")
                elif row['variation_pct'] > 0:
                    st.markdown("↗️ Légère hausse")
                elif row['variation_pct'] < -1:
                    st.markdown("📉 Forte baisse")
                elif row['variation_pct'] < 0:
                    st.markdown("↘️ Légère baisse")
                else:
                    st.markdown("➡️ Stable")
            
            st.markdown("---")
        
        return auto_refresh
    
    def create_market_overview(self):
        """Vue d'ensemble du marché en temps réel"""
        st.markdown('<h3 class="section-header">🌍 VUE MARCHÉ TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        if self.current_data.empty:
            st.warning("Chargement des données en cours...")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Carte thermique des performances
            performance_data = self.current_data[['symbole', 'variation_pct']].copy()
            performance_data['abs_variation'] = abs(performance_data['variation_pct'])
            
            fig = px.treemap(performance_data,
                           path=['symbole'],
                           values='abs_variation',
                           color='variation_pct',
                           color_continuous_scale='RdYlGn',
                           title='Carte Thermique des Performances',
                           hover_data=['variation_pct'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Graphique de répartition sectorielle
            sector_data = self.current_data.groupby('secteur').agg({
                'prix_actuel': 'count',
                'variation_pct': 'mean',
                'volume': 'sum'
            }).reset_index()
            
            fig = px.pie(sector_data, 
                        values='volume', 
                        names='secteur',
                        title='Répartition par Volume',
                        color='secteur',
                        color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_sidebar_controls(self):
        """Crée les contrôles de la sidebar"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES TEMPS RÉEL")
        
        # Paramètres de mise à jour
        st.sidebar.markdown("### ⚡ Fréquence de mise à jour")
        update_freq = st.sidebar.slider("Secondes entre mises à jour", 
                                       min_value=5, max_value=60, value=10)
        
        # Alertes de prix
        st.sidebar.markdown("### 🔔 Alertes de Prix")
        if not self.current_data.empty:
            alert_stock = st.sidebar.selectbox("Action à surveiller:", 
                                             list(self.entreprises.keys()))
            current_price = self.current_data[self.current_data['symbole'] == alert_stock]['prix_actuel'].iloc[0]
            alert_price = st.sidebar.number_input("Prix d'alerte ($)", 
                                                min_value=0.0, 
                                                value=float(current_price))
            
            # Vérifier si l'alerte est déclenchée
            if current_price >= alert_price * 1.05:
                st.sidebar.error(f"🚨 {alert_stock} a dépassé {alert_price}$!")
            elif current_price <= alert_price * 0.95:
                st.sidebar.error(f"🚨 {alert_stock} est tombé sous {alert_price}$!")
        
        # Indices de référence
        st.sidebar.markdown("### 💹 INDICES LIVE")
        
        indices = {
            'NASDAQ': '^IXIC',
            'S&P 500': '^GSPC',
            'DOW JONES': '^DJI',
            'RUSSELL 2000': '^RUT'
        }
        
        for indice_name, indice_ticker in indices.items():
            try:
                indice_data = yf.Ticker(indice_ticker)
                hist = indice_data.history(period='1d', interval='1m')
                if not hist.empty:
                    valeur = hist['Close'].iloc[-1]
                    ouverture = hist['Open'].iloc[0]
                    variation = ((valeur - ouverture) / ouverture) * 100
                    
                    st.sidebar.metric(
                        indice_name,
                        f"{valeur:,.0f}",
                        f"{variation:+.2f}%"
                    )
            except:
                st.sidebar.write(f"{indice_name}: Chargement...")
        
        return update_freq

    def run_dashboard(self):
        """Exécute le dashboard temps réel"""
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Contrôles sidebar
        update_freq = self.create_sidebar_controls()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Tableau Live", 
            "📈 Graphiques", 
            "🌍 Vue Marché",
            "⚙️ Paramètres"
        ])
        
        with tab1:
            auto_refresh = self.create_real_time_table()
        
        with tab2:
            self.create_real_time_charts()
        
        with tab3:
            self.create_market_overview()
        
        with tab4:
            st.markdown("## ⚙️ PARAMÈTRES TEMPS RÉEL")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔧 Configuration")
                st.write(f"**Fréquence actuelle:** {update_freq} secondes")
                st.write(f"**Dernière mise à jour:** {self.last_update.strftime('%H:%M:%S')}")
                st.write(f"**Entreprises surveillées:** {len(self.entreprises)}")
                
                if st.button("🔄 Forcer la mise à jour maintenant"):
                    self.update_live_data()
                    st.rerun()
            
            with col2:
                st.markdown("### 📡 Statut des données")
                st.write("**Source:** Yahoo Finance API")
                st.write("**Latence:** 1-2 minutes")
                st.write("**Couverture:** Données intraday")
                st.write("**Période:** Données minute par minute")
        
        # Mise à jour automatique
        if auto_refresh:
            time.sleep(update_freq)
            self.update_live_data()
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = RealTimeGAFAMDashboard()
    dashboard.run_dashboard()