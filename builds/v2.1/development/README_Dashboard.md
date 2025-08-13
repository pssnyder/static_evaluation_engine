# Chess Engine Analysis Dashboard

A comprehensive, interactive dashboard for analyzing and debugging the Cece chess engine. This dashboard provides visual analysis tools, PST heatmaps, puzzle testing capabilities, and code metrics.

## 🚀 Quick Start

### Option 1: Automated Setup
1. Run `refresh_dashboard.bat` from the `docs/` directory
2. This will automatically extract data and open the dashboard

### Option 2: Manual Setup
1. Extract engine data: `python extract_engine_data.py`
2. Open `Enhanced_Engine_Analysis_Dashboard.html` in your browser

## 📊 Features

### 🎯 Evaluation Analysis Tab
- **PST Heatmaps**: Visual representation of piece-square tables with color-coded values
  - Red/Orange = High values (hot squares)
  - Blue/Purple = Low values (cold squares)
- **Dynamic Piece Selection**: Switch between different piece types
- **Real-time Value Display**: Hover over squares to see exact values

### 🧩 Puzzle Analysis Tab
- **Filter by Rating**: Adjust minimum puzzle rating
- **Theme Selection**: Filter puzzles by tactical themes
- **Puzzle Browser**: View sample puzzles with FEN positions
- **Integration**: Click puzzles to load them in the Position Editor

### ♟️ Position Analysis Tab
- **FEN Editor**: Input custom positions for analysis
- **Position Comparison**: Compare two positions side-by-side
- **Move Analysis**: Analyze specific moves and positions

### 📈 Statistics Tab
- **Code Metrics**: Lines of code, function counts, class counts
- **File Analysis**: Breakdown by source file
- **Evaluation Function Tracking**: Monitor evaluation components

### 📚 Documentation Tab
- **Architecture Overview**: Engine structure and design decisions
- **Configuration Guide**: How to modify engine parameters
- **Usage Examples**: Common analysis workflows

## 🔧 Data Sources

The dashboard reads data from:
- `evaluation.py` - PST tables, piece values, weights
- `engine.py` - Core engine logic and statistics
- `lichess_db_puzzle.csv` - Puzzle database for testing
- Analysis results from `results/analysis/` directory

## 🔄 Refreshing Data

### Automatic Refresh
- Run `refresh_dashboard.bat` anytime you modify engine code
- This will re-extract all data and refresh the dashboard

### Manual Refresh
1. Run: `python extract_engine_data.py`
2. Refresh the browser page (F5)

## 📁 File Structure

```
docs/
├── Enhanced_Engine_Analysis_Dashboard.html  # Main dashboard
├── extract_engine_data.py                   # Data extraction script
├── refresh_dashboard.bat                    # Automated refresh
└── README_Dashboard.md                      # This file

results/analysis/
├── dashboard_data.json                      # Combined data file
├── evaluation_config.json                  # PST tables and weights
├── code_statistics.json                    # Code metrics
└── puzzle_metadata.json                    # Puzzle information
```

## 🎨 Visual Design

### Color Schemes
- **PST Heatmaps**: Blue (cold) → Yellow → Orange → Red (hot)
- **Success States**: Green tones
- **Warning States**: Yellow/Orange tones
- **Error States**: Red tones
- **Info States**: Blue tones

### UI Layout
- **Tabbed Interface**: Clean separation of analysis areas
- **Responsive Design**: Works on different screen sizes
- **Interactive Elements**: Hover effects and click handlers
- **Real-time Updates**: Data refreshes without page reload

## 🔍 Advanced Usage

### Debug Console
The dashboard exposes debug functions in the browser console:
```javascript
// Access loaded data
debugDashboard.data()          // All dashboard data
debugDashboard.evaluation()    // Evaluation config
debugDashboard.puzzles()       // Puzzle metadata

// Reload data
debugDashboard.reload()        // Refresh all data

// Load sample puzzles
debugDashboard.loadSample()    // Display sample puzzles
```

### Custom Analysis
1. Modify `extract_engine_data.py` to extract additional metrics
2. Update the dashboard JavaScript to display new data
3. Use the tab system to add new analysis views

## 🛠️ Troubleshooting

### Data Loading Issues
- Ensure `extract_engine_data.py` runs without errors
- Check that `results/analysis/` directory exists and contains JSON files
- Verify file paths in the HTML are correct for your setup

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Edge) are recommended
- Local file access may require specific browser settings
- Use a local web server for best compatibility

### Performance
- Large puzzle databases may slow initial loading
- PST heatmap rendering is optimized for 64-square boards
- Data extraction is limited to 1000 puzzles for performance

## 🎯 Best Practices

### Regular Workflow
1. Make engine changes
2. Run `refresh_dashboard.bat`
3. Analyze changes in the dashboard
4. Use PST heatmaps to validate piece-square tables
5. Test with puzzles to verify tactical improvements

### Debugging Process
1. Check Statistics tab for code changes
2. Use Evaluation tab to verify PST modifications
3. Use Puzzle tab to test tactical understanding
4. Use Position tab for specific position analysis

## 🔗 Integration

### With Engine Development
- Dashboard reflects real-time engine configuration
- PST changes immediately visible in heatmaps
- Code statistics track development progress

### With Testing
- Puzzle results can inform engine improvements
- Position analysis helps debug specific cases
- Performance metrics guide optimization efforts

---

**Note**: This dashboard is designed for static analysis of engine code and configuration. For live engine testing, use the UCI interface and dedicated chess GUIs.
