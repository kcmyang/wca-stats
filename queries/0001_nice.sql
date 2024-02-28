select
    personId,
    sum(num69) as gts
from
    (
        select
            personId,
            if(value1 % 100 = 69, 1, 0) + if(value2 % 100 = 69, 1, 0) + if(value3 % 100 = 69, 1, 0) + if(value4 % 100 = 69, 1, 0) + if(value5 % 100 = 69, 1, 0) as num69
        from
            results
        where
            eventId != '333mbf'
    ) as t
group by
    personId
order by
    gts desc
limit
    50;
