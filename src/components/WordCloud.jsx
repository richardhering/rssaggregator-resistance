import React, { useEffect, useRef, useState } from "react";
import anychart from "anychart";

// Function to convert the data into the required format
function convertToWordCloudFormat(data) {
    if (typeof data !== "object" || data === null) {
      throw new Error("Input data should be an object.");
    }
  
    const formattedData = Object.keys(data)
      .filter(key => key.trim() !== "") // Filter out empty strings
      .map((key) => ({
        x: key,    // Tag name (e.g., "Persian")
        value: data[key] // Frequency (e.g., 121000000)
      }));
  
    console.log("Formatted Data:", formattedData); // For debugging
  
    return formattedData;
  }
  

export function WordCloud({ tags, onTagClick }) {
    const chartContainerRef = useRef(null);
    useEffect(() => {
        
    

      const formattedTags = convertToWordCloudFormat(tags);
  
      // Ensure each tag is an object with 'text' and 'value' properties, or map them if needed
      
  
      const chart = anychart.tagCloud(formattedTags);
      chart.angles([0]);
      chart.colorRange(true);
      chart.colorRange().length("80%");

      chart.listen("pointClick", function (e) {
        const tagText = e.point.get("x"); // Get the clicked tag's text
        if (onTagClick) {
          onTagClick(tagText); // Pass the tagText to the parent
        }
      });
  
      if (chartContainerRef.current) {
        chart.container(chartContainerRef.current);
        chart.draw();
      }
  
      // Optional: Clean up chart on unmount
      return () => {
        chart.dispose();
      };
    }, [tags, onTagClick]); // Re-run the effect if `tags` changes
  
    return <div ref={chartContainerRef} style={{ width: "100%", height: "500px" }} />;
  }