import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class CreateCsvFile {
    private static void addDataToCSV(SortedMap<String, SortedMap<Integer, Integer>> placesByYears) {
        try {
            BufferedWriter writer = Files.newBufferedWriter(Paths.get("places_by_years.csv"));
            CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT
                    .withHeader("Place", "Year", "Occurrences"));
            for (String key : placesByYears.keySet()) {
                SortedMap<Integer, Integer> yearsWithOccurrences = placesByYears.get(key);
                for (Integer year : yearsWithOccurrences.keySet()){
                    Integer occurrences = yearsWithOccurrences.get(year);
                    String[] data = new String[]{key.substring(1, key.length() - 1).replace("\\",""),
                            year.toString(), occurrences.toString()};
                    csvPrinter.printRecord(Arrays.asList(data));
                }
            }

            writer.close();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException {
        JsonObject jsonObject = new JsonParser().parse(new FileReader("places_with_data.json")).getAsJsonObject();
        SortedMap<String, SortedMap<Integer, Integer>> placesByYears = new TreeMap<>();
        for (Map.Entry<String, JsonElement> stringJsonElementEntry : jsonObject.entrySet()) {
            JsonElement obj = new JsonParser().parse(String.valueOf(stringJsonElementEntry.getValue()));
            JsonArray placesArray = obj.getAsJsonObject().get("places").getAsJsonArray();
            JsonElement year = obj.getAsJsonObject().get("year");
            if (year != null && placesArray.size() > 0) {
                for (int i = 0; i < placesArray.size(); i++) {
                    JsonElement place = placesArray.get(i);
                    String placeStr = place.toString();
                    SortedMap<Integer, Integer> placeYear;
                    if (placesByYears.containsKey(placeStr)) {
                        placeYear = placesByYears.get(placeStr);
                        if (placeYear.containsKey(year.getAsInt())) {
                            int currVal = placeYear.get(year.getAsInt());
                            currVal++;
                            placeYear.put(year.getAsInt(), currVal);
                        } else {
                            placeYear.put(year.getAsInt(), 1);
                        }
                    } else {
                        placeYear = new TreeMap<>();
                        placeYear.put(year.getAsInt(), 1);
                    }
                    placesByYears.put(placeStr, placeYear);
                }
            }
        }
        addDataToCSV(placesByYears);
    }
}
