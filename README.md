# JobSearch

Setup for a database of job applications using SQLite with some useful functions to store the data and access it.

It contains 5 tables:
- applications containing the data for applications (date, description, company, city, URL, etc.)
- companies containing the names for company ids
- events containing events such as phone calls, interviews, etc.
- event_types containing the event_types for event ids
- status containing the statuses for status ids