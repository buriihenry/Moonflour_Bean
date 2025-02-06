// babel.config.js
module.exports = function (api) {
    api.cache(true);
    return {
      presets: ['babel-preset-expo'],
      plugins: [
        // Make sure NativeWind's babel plugin comes before Expo Router's plugin
        "nativewind/babel",
        'expo-router/babel'
      ],
    };
  };
