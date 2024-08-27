import React, { useState } from "react";
import "./App.css";

function App() {
  const [city, setCity] = useState<string>('');
  const [weatherData, setWeatherData] = useState<any>();
  const [weatherTodayData, setTodayWeatherData] = useState<any>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch(`https://api.journey.skillreactor.io/r/f/weather`);
    const data = await response.json();

    const cityData = data.filter((rec: any) => rec.city === city);
    // console.log(cityData)

    const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
    const todayWeather = cityData.find((day: any) => day.dayOfWeek === today);
    // console.log(todayWeather)

    setWeatherData(cityData);
    setTodayWeatherData(todayWeather);
  };
  return (
    <div className="App">

      <form onSubmit={handleSubmit}>
        <label htmlFor="cityInput">Enter City Name: </label>
        <input type="text" id="cityInput" value={city} onChange={(e) => setCity(e.target.value)} required />
        <button type="submit" id="submitBtn">Search</button>
      </form>

      {weatherTodayData && (
        <div>
          <div id="mainCity">{weatherTodayData.city}</div>
          <div id="mainWeekday">{weatherTodayData.dayOfWeek}</div>
          <div id="mainTemperature">{weatherTodayData.temperature}</div>
          <div id="mainHumidity">{weatherTodayData.humidity}</div>
          <div id="mainWindSpeed">{weatherTodayData.windSpeed} m/s</div>
        </div>
      )}

      {/* Display weather forecast for the next 6 days */}
      {weatherData && weatherData.slice(0, 6).map((day:any) => (
        <div id={`data_${day.dayOfWeek.toLowerCase()}`} key={day.dayOfWeek}>
          <h3 className="weekDay">{day.dayOfWeek}</h3>
          <p className="temperature">{day.temperature}</p>
          <p className="humidity">{day.humidity}</p>
          <p className="windSpeed">{day.windSpeed} m/s</p>
        </div>
      ))}

    </div>
  );
}

export default App;
