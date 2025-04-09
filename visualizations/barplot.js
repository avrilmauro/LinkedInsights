    const salaryBuckets = [
      "Under $60k",
      "$60k-$85k",
      "$85k-$110k",
      "$110k-$150k",
      "$150k-$200k",
      "$200k+"
    ];

    const bucketMapping = {
      "150k": "$150k-$200k",
      "200k": "$200k+"
    };

    d3.csv("linkedin_skills_df.csv", d => ({
      salary_bucket: bucketMapping[d.salary_bucket] || d.salary_bucket,
      skill_name: d.skill_name,
      count: +d.count
    })).then(data => {
      const svg = d3.select("svg");
      const margin = { top: 40, right: 200, bottom: 70, left: 80 };
      const width = +svg.attr("width") - margin.left - margin.right;
      const height = +svg.attr("height") - margin.top - margin.bottom;
      const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

      const skillTotals = {};
      data.forEach(d => {
        skillTotals[d.skill_name] = (skillTotals[d.skill_name] || 0) + d.count;
      });

      const sortedSkills = Object.entries(skillTotals)
        .sort((a, b) => b[1] - a[1])
        .map(d => d[0]);

      const tableauColors = [
        "#6388b4", "#FFA51F", "#ef6f6a", "#55ad89",
        "#309143", "#c3bc3f", "#bb7693",
        "#995688", "#b66353",
      ];

      const color = d3.scaleOrdinal()
        .domain(sortedSkills)
        .range(tableauColors);

      const dataGrouped = d3.groups(data, d => d.salary_bucket);
      const stackedData = [];

      for (const [bucket, entries] of dataGrouped) {
        const row = { salary_bucket: bucket };
        entries.forEach(d => {
          row[d.skill_name] = d.count;
        });
        stackedData.push(row);
      }

      const stack = d3.stack()
        .keys(sortedSkills)
        .order(d3.stackOrderNone)
        .offset(d3.stackOffsetNone);

      const series = stack(stackedData);

      const x = d3.scaleBand()
        .domain(salaryBuckets)
        .range([0, width])
        .padding(0.2);

      const y = d3.scaleLinear()
        .domain([0, d3.max(stackedData, d =>
          sortedSkills.reduce((sum, k) => sum + (d[k] || 0), 0)
        )])
        .nice()
        .range([height, 0]);

      g.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("font-size", "12px")
        .style("font-family", "Roboto")
        .style("font-weight", "bold")
        .attr("dy", "1.5em");

      g.append("text")
        .attr("x", width / 2)
        .attr("y", height + 60)
        .attr("text-anchor", "middle")
        .style("font-family", "Poppins")
        .text("Salary Bucket");

      g.append("g")
        .call(d3.axisLeft(y));

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -60)
        .attr("x", -height / 2)
        .attr("text-anchor", "middle")
        .style("font-family", "Poppins")
        .text("Occurrences");

      const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

      const layers = g.selectAll("g.layer")
        .data(series)
        .join("g")
          .attr("class", "layer")
          .attr("fill", d => color(d.key));

      layers.selectAll("rect")
        .data(d => d)
        .join("rect")
          .attr("x", d => x(d.data.salary_bucket))
          .attr("y", d => y(d[1]))
          .attr("height", d => y(d[0]) - y(d[1]))
          .attr("width", x.bandwidth())
          .on("mouseover", function (event, d) {
            const skill = d3.select(this.parentNode).datum().key;
            const count = d.data[skill] || 0;
            tooltip.transition().duration(200).style("opacity", 0.9);
            tooltip.html(`<strong>${skill}</strong><br/>Count: ${count}`)
              .style("left", (event.pageX + 10) + "px")
              .style("top", (event.pageY - 28) + "px");
          })
          .on("mouseout", () => {
            tooltip.transition().duration(500).style("opacity", 0);
          });

      layers.selectAll("text")
        .data(d => d)
        .join("text")
          .text(function(d) {
            const skill = d3.select(this.parentNode).datum().key;
            const count = d.data[skill] || 0;
            return count > 0 ? count : "";
          })
          .attr("x", d => x(d.data.salary_bucket) + x.bandwidth() / 2)
          .attr("y", d => {
            const heightSegment = y(d[0]) - y(d[1]);
            return heightSegment > 12 ? y(d[1]) + heightSegment / 2 + 4 : -100;
          })
          .attr("text-anchor", "middle")
          .attr("font-size", "10px")
          .attr("fill", "white")
          .style("pointer-events", "none");

      const legend = svg.append("g")
        .attr("class", "legend")
        .attr("transform", `translate(${width + margin.left + 30},${margin.top})`);

      legend.append("text")
        .attr("x", 0)
        .attr("y", -10)
        .attr("font-weight", "bold")
        .text("Skill");

      sortedSkills.forEach((skill, i) => {
        const row = legend.append("g")
          .attr("transform", `translate(0, ${i * 22})`);

        row.append("rect")
          .attr("width", 20)
          .attr("height", 14)
          .attr("fill", color(skill));

        row.append("text")
          .attr("x", 26)
          .attr("y", 11)
          .style("font-size", "12px")
          .style("dominant-baseline", "middle")
          .text(skill);
      });
    });
