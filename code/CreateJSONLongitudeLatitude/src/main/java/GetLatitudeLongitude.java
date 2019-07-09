import com.google.gson.*;

import java.io.*;
import java.util.HashMap;
import java.util.Map;

public class GetLatitudeLongitude {
    private static void createJsonFile(JsonObject jsonObjectAsArray) throws IOException {
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            String json = gson.toJson(jsonObjectAsArray);
            Writer out = new BufferedWriter(new OutputStreamWriter(
                    new FileOutputStream(new File("places_with_data_and_lon_lat.json")), "UTF8"));
            out.append(json);
            out.flush();
            out.close();
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        /* Saving all the places with longitude and latitude in order to improve performance
        and perform less operations with the network.
         */
        HashMap<String, Double[]> placesWithLonLat = new HashMap<String, Double[]>();
        Map<String, Double> coords;
        Double lat, lon;
        JsonObject jsonObject = new JsonParser().parse(new FileReader("places_with_data.json")).getAsJsonObject();
        JsonObject jsonObjectAsArray = new JsonObject();
        for (Map.Entry<String, JsonElement> stringJsonElementEntry : jsonObject.entrySet()) {
            JsonElement obj = new JsonParser().parse(String.valueOf(stringJsonElementEntry.getValue()));
            JsonArray placesArray = obj.getAsJsonObject().get("places").getAsJsonArray();
            JsonArray updatedPlacesArray = new JsonArray();
            for (int i = 0; i < placesArray.size(); i++){
                JsonArray place = placesArray.get(i).getAsJsonArray();
                JsonElement placeHeb = place.get(0), placeEng = place.get(1);
                String placeStrEng = placeEng.toString();
                placeStrEng = placeStrEng.substring(1, placeStrEng.length() - 1);
                String placeStrHeb = placeHeb.toString();
                placeStrHeb = placeStrHeb.substring(1, placeStrHeb.length() - 1);
                if (placeStrHeb.contains("רחובות") || placeStrHeb.contains("שדרות") || placeStrHeb.contains("חדרה")){
                    placeStrEng = placeStrHeb;
                }
                if (!placesWithLonLat.containsKey(placeStrEng)){
                    Thread.sleep(1000); // Waiting 1 second before request, otherwise the server may block us.
                    coords = OpenStreetMapUtils.getInstance().getCoordinates(placeStrEng);
                    placesWithLonLat.put(placeStrEng, new Double[]{coords.get("lat"), coords.get("lon")});
                }
                Double[] latLon = placesWithLonLat.get(placeStrEng);
                lat = latLon[0];
                lon = latLon[1];
                if (lat != null && lon != null){
                    JsonObject placeJsonObj = new JsonObject();
                    placeJsonObj.addProperty("place", placeStrHeb);
                    placeJsonObj.addProperty("latitude", lat);
                    placeJsonObj.addProperty("longitude", lon);
                    updatedPlacesArray.add(placeJsonObj);
                }
            }
            JsonObject tempJsonObject = obj.getAsJsonObject();
            tempJsonObject.remove("places");
            tempJsonObject.add("places", updatedPlacesArray);
            jsonObjectAsArray.add(stringJsonElementEntry.getKey() ,tempJsonObject);
        }
        createJsonFile(jsonObjectAsArray);
    }
}
