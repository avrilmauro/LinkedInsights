    const svg = d3.select("svg"),
      margin = { top: 40, right: 20, bottom: 80, left: 100 },
      width = +svg.attr("width") - margin.left - margin.right,
      height = +svg.attr("height") - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    function formatMoney(val) {
      if (val >= 100000) return "$" + Math.round(val / 1000) + "K";
      return "$" + (val >= 1000 ? (val / 1000).toFixed(val % 1000 === 0 ? 0 : 1) + "K" : val);
    }

    d3.csv("linkedin_df.csv").then(data => {
      data = data
        .filter(d => d.formatted_experience_level && !isNaN(d.normalized_salary))
        .map(d => ({
          level: d.formatted_experience_level.trim(),
          salary: +d.normalized_salary
        }));

      const levelMap = {
        "Internship": "Internship",
        "Entry level": "Entry Level",
        "Associate": "Associate",
        "Mid-Senior level": "Mid-Senior Level",
        "Director": "Director",
        "Executive": "Executive"
      };

      const orderedLevels = Object.keys(levelMap);

      const grouped = d3.group(data, d => d.level);
      const boxData = orderedLevels.map(level => {
        const values = grouped.get(level) || [];
        const salaries = values.map(d => d.salary).sort(d3.ascending);
        const q1 = d3.quantile(salaries, 0.25);
        const median = d3.quantile(salaries, 0.5);
        const q3 = d3.quantile(salaries, 0.75);
        const iqr = q3 - q1;
        const min = d3.min(salaries.filter(s => s >= q1 - 1.5 * iqr));
        const max = d3.max(salaries.filter(s => s <= q3 + 1.5 * iqr));

        return { level: levelMap[level], q1, median, q3, min, max };
      });

      const x = d3.scaleBand()
        .domain(boxData.map(d => d.level))
        .range([0, width])
        .padding(0.4);

      const y = d3.scaleLinear()
        .domain([0, d3.max(boxData, d => d.max) * 1.1])
        .range([height, 0])
        .nice();

      g.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y)
          .tickSize(-width)
          .tickFormat("")
        );

      g.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        .style("font-size", "12px")
        .style("font-family", "Roboto")
        .style("font-weight", "bold")
        .attr("dy", "1.5em");

      g.append("g")
        .call(d3.axisLeft(y).tickFormat(formatMoney))
        .select(".domain")
        .remove();

      // X axis label
      svg.append("text")
        .attr("class", "axis-label")
        .attr("x", margin.left + width / 2)
        .attr("y", height + margin.top + 60)
        .attr("text-anchor", "middle")
        .text("Experience Level");

      // Y axis label
      svg.append("text")
        .attr("class", "axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -(margin.top + height / 2))
        .attr("y", 30)
        .attr("text-anchor", "middle")
        .text("Salary");

      const boxWidth = x.bandwidth();

      g.selectAll(".box")
        .data(boxData)
        .enter()
        .append("rect")
        .attr("class", "box")
        .attr("x", d => x(d.level))
        .attr("y", d => y(d.q3))
        .attr("width", boxWidth)
        .attr("height", d => y(d.q1) - y(d.q3));

      g.selectAll(".median")
        .data(boxData)
        .enter()
        .append("line")
        .attr("class", "median")
        .attr("x1", d => x(d.level))
        .attr("x2", d => x(d.level) + boxWidth)
        .attr("y1", d => y(d.median))
        .attr("y2", d => y(d.median));

      g.selectAll(".label-median")
        .data(boxData)
        .enter()
        .append("text")
        .attr("x", d => x(d.level) + boxWidth / 2)
        .attr("y", d => y(d.median) - 6)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "white")
        .text(d => d.level === "Internship" ? "" : formatMoney(d.median));

      g.selectAll(".whisker-top")
        .data(boxData)
        .enter()
        .append("line")
        .attr("class", "whisker")
        .attr("x1", d => x(d.level) + boxWidth / 2)
        .attr("x2", d => x(d.level) + boxWidth / 2)
        .attr("y1", d => y(d.q3))
        .attr("y2", d => y(d.max));

      g.selectAll(".whisker-bottom")
        .data(boxData)
        .enter()
        .append("line")
        .attr("class", "whisker")
        .attr("x1", d => x(d.level) + boxWidth / 2)
        .attr("x2", d => x(d.level) + boxWidth / 2)
        .attr("y1", d => y(d.q1))
        .attr("y2", d => y(d.min));

      g.selectAll(".min-dot")
        .data(boxData)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.level) + boxWidth / 2)
        .attr("cy", d => y(d.min))
        .attr("r", 2.5)
        .attr("fill", "black");

      g.selectAll(".max-dot")
        .data(boxData)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.level) + boxWidth / 2)
        .attr("cy", d => y(d.max))
        .attr("r", 2.5)
        .attr("fill", "black");

      g.selectAll(".label-min")
        .data(boxData)
        .enter()
        .append("text")
        .attr("x", d => x(d.level) + boxWidth / 2)
        .attr("y", d => y(d.min) + 16)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "gray")
        .text(d => "Min: " + formatMoney(d.min));

      g.selectAll(".label-max")
        .data(boxData)
        .enter()
        .append("text")
        .attr("x", d => x(d.level) + boxWidth / 2)
        .attr("y", d => y(d.max) - 8)
        .attr("text-anchor", "middle")
        .attr("font-size", "10px")
        .attr("fill", "gray")
        .text(d => "Max: " + formatMoney(d.max));
    });