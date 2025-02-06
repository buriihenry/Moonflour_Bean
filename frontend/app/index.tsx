import { View, Text } from 'react-native';

export default function Index() {
  return (
    <View className="flex-1 justify-center items-center bg-red-500">
      <Text className="text-4xl text-white font-bold p-4 bg-black rounded-lg m-4">
        Hey You from Moonflour!
      </Text>
      <Text className="text-2xl text-yellow-400 underline">
        Tailwind Test
      </Text>
    </View>
  );
}