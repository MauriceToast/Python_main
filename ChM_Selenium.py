all_matches_data = []
    print(f"\nScraping data for: ")
    matches_data = scrape_month(driver)
    all_matches_data.extend(matches_data)

    if all_matches_data:
        write_matches_to_csv(all_matches_data, 'ChM_matches.csv')
        print(f"Total matches written to CSV: {len(all_matches_data)}")
    else:
        print("No data collected for any month")
