# MovieLensAnalyze
Dataset: http://grouplens.org/datasets/movielens/

#Problem Statement
./analyze_movies.py (Gender|Age) <number>

The first argument is the grouping. For example, if gender is selected, then two lists will be output: top movies as rated by men, and top movies as rated by women. If agegroup is selected, 7 lists should be output, as specified in the dataset README. The <number> is how many to output. If there are fewer than <number> movies, output them all.
An example invocation would, therefore be "./analyze_movies.py age 20"

#Defining the concept of **Top** movies
The problem statement above is very vague in terms of defining what **top** movies mean. One simple way would be to order by 
average rating of the movie. However, the problem with this is that our belief with movies that are rated by very few number of
users can skew the ordering. Consider for example a movie X that has a single rating of "5". Clearly, the average rating of this
 movie is going to be "5" as well. However, since only one user rated this movie, our belief in this should be very low. 
 To account for this, number of users should be reflected in the score. Naive way would be to simple multiply average rating 
 with the number of users ( to got total rating). Again, this has the problem that movies that are rated by a lot of people
 will get higher rating than rating watched by fewer number of people even if the average rating of former is less than the latter.
 To tackle this, I multiply with the logarithm of number of users instead. The idea is that out belief should linearly go up with the number 
 of users initial, however, after a limit it should plateau out.
 

#Note

*   Although **sqllite3** is part of standard library, however, I think using it will defeat the purpose so I have used my own class. It will be pretty simple to construct though

```sql
    CREATE TABLE movielens 
    AS
    SELECT 
         r.*,
         u.*,
         m.*
    FROM 
        ratings AS r
    JOIN
        movies AS m
    ON
        r.MovieID = m.MovieID
    JOIN
        users AS u
    ON 
        u.UserID = r.UserID;
        
        
    SELECT 
        Gender,
        Title,
        SumRating/NumUsers AS AvgRating,
        NumUsers,
        (SumRating/NumUsers) * LOG(NumUsers) AS Score
    From
    (
        SELECT
            Gender,
            Title,
            sum(Rating) AS SumRating,
            count(1) AS NumUsers
        FROM movielens
        GROUP BY
            Gender
    ) AS x
    ORDER BY
        Score DESC
    LIMIT 20;
```

*   No Machine Learning is used.
