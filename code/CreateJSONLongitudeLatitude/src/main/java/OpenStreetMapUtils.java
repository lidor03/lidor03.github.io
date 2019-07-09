import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import org.apache.log4j.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.json.simple.parser.JSONParser;

import javax.net.ssl.HttpsURLConnection;

// Based on this tutorial, with some changes:
// http://julien.gunnm.org/geek/programming/2015/09/13/how-to-get-geocoding-information-in-java-without-google-maps-api/

class OpenStreetMapUtils {

    private final static Logger log = Logger.getLogger("OpenStreeMapUtils");

    private static OpenStreetMapUtils instance = null;

    private OpenStreetMapUtils() {
        JSONParser jsonParser = new JSONParser();
    }

    static OpenStreetMapUtils getInstance() {
        if (instance == null) {
            instance = new OpenStreetMapUtils();
        }
        return instance;
    }

    private String getRequest(String url) throws Exception {
        final URL obj = new URL(url);
        final HttpsURLConnection con = (HttpsURLConnection) obj.openConnection();

        con.setRequestMethod("GET");

        if (con.getResponseCode() != 200) {
            return null;
        }

        BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
        String inputLine;
        StringBuilder response = new StringBuilder();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        return response.toString();
    }

    Map<String, Double> getCoordinates(String address) {
        Map<String, Double> res;
        String query;
        String[] split = address.split(" ");
        String queryResult = null;

        res = new HashMap<String, Double>();

        query = "https://nominatim.openstreetmap.org/search?q=";

        if (split.length == 0) {
            return null;
        }

        for (int i = 0; i < split.length; i++) {
            if (split[i].contains(",")){
                split[i] = split[i].replace(",", "");
            }
            query += (split[i]);
            if (i < (split.length - 1)) {
                query += "+";
            }
        }
        query += ("&format=json&addressdetails=1");

        try {
            queryResult = getRequest(query);
        } catch (Exception e) {
            log.error("Error when trying to get data with the following query " + query);
        }

        if (queryResult == null) {
            return null;
        }

        Object obj = JSONValue.parse(queryResult);

        if (obj instanceof JSONArray) {
            JSONArray array = (JSONArray) obj;
            if (array.size() > 0) {
                JSONObject jsonObject = (JSONObject) array.get(0);
                String lon = (String) jsonObject.get("lon");
                String lat = (String) jsonObject.get("lat");
                res.put("lon", Double.parseDouble(lon));
                res.put("lat", Double.parseDouble(lat));
            }
        }
        return res;
    }
}
