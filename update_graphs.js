import { createClient } from "@supabase/supabase-js";

// Initialize Supabase client with direct environment variables
const supabaseUrl = "https://aqfldxwqjnwwfbsrjnwz.***REMOVED***"; // Your Supabase project URL
const supabaseAnonKey =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxZmxkeHdxam53d2Zic3JqbndaIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA0MzI5NjAsImV4cCI6MjAyNjAwODk2MH0.Ry-nWxrZTkfMB2c9QYoGg0MHgBAOWPNl_Ov_xVlQEXg"; // Your public anon key

const supabase = createClient(supabaseUrl, supabaseAnonKey);

const USER_ID = "973fe17b-cd5c-4595-bcd9-260c411e002b";

async function updateGraphs() {
  try {
    // First, let's check existing graphs
    const { data: existingGraphs, error: fetchError } = await supabase
      .from("graphs")
      .select("*");

    if (fetchError) throw fetchError;
    console.log("Found graphs:", existingGraphs?.length || 0);

    // Update all graphs to belong to the specified user
    const { data, error } = await supabase
      .from("graphs")
      .update({ user_id: USER_ID })
      .is("user_id", null)
      .select();

    if (error) throw error;

    console.log("Successfully updated graphs:", data?.length || 0);
  } catch (error) {
    console.error("Error updating graphs:", error);
  } finally {
    process.exit();
  }
}

updateGraphs();
