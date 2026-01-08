# Pagination UI Implementation Guide

## Overview
Pagination has been added to the flood records table to handle large datasets efficiently.

## Backend Implementation ✅ DONE

### Changes Made:
1. **Import Added**: `from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger`
2. **Query Parameters**:
   - `?page=N` - Navigate to page N
   - `?per_page=N` - Show N records per page (default: 20, max: 100)

### Context Variables Available in Template:
```python
{
    'flood_records': [...],           # Current page records (list)
    'flood_records_page': page_obj,   # Page object with methods
    'paginator': paginator_obj,       # Paginator with stats
}
```

### Page Object Methods:
```python
flood_records_page.has_previous()      # True if not first page
flood_records_page.has_next()          # True if not last page
flood_records_page.previous_page_number()  # Previous page number
flood_records_page.next_page_number()      # Next page number
flood_records_page.number              # Current page number
```

### Paginator Object Properties:
```python
paginator.num_pages       # Total number of pages
paginator.count           # Total number of records
paginator.page_range      # Range object for page numbers
```

## Frontend Implementation (NEEDED)

### Option 1: Simple Previous/Next Buttons
Add this HTML where you display flood records:

```html
<!-- Pagination Controls -->
<div class="pagination-container" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">
    <div class="pagination-info" style="color: #64748b; font-size: 14px;">
        Showing {{ flood_records|length }} of {{ paginator.count }} records
        (Page {{ flood_records_page.number }} of {{ paginator.num_pages }})
    </div>
    
    <div class="pagination-controls" style="display: flex; gap: 10px;">
        {% if flood_records_page.has_previous %}
            <a href="?page=1" class="btn btn-sm btn-outline-primary">
                <i class="fa fa-angle-double-left"></i> First
            </a>
            <a href="?page={{ flood_records_page.previous_page_number }}" class="btn btn-sm btn-outline-primary">
                <i class="fa fa-angle-left"></i> Previous
            </a>
        {% else %}
            <button class="btn btn-sm btn-outline-secondary" disabled>
                <i class="fa fa-angle-double-left"></i> First
            </button>
            <button class="btn btn-sm btn-outline-secondary" disabled>
                <i class="fa fa-angle-left"></i> Previous
            </button>
        {% endif %}
        
        {% if flood_records_page.has_next %}
            <a href="?page={{ flood_records_page.next_page_number }}" class="btn btn-sm btn-outline-primary">
                Next <i class="fa fa-angle-right"></i>
            </a>
            <a href="?page={{ paginator.num_pages }}" class="btn btn-sm btn-outline-primary">
                Last <i class="fa fa-angle-double-right"></i>
            </a>
        {% else %}
            <button class="btn btn-sm btn-outline-secondary" disabled>
                Next <i class="fa fa-angle-right"></i>
            </button>
            <button class="btn btn-sm btn-outline-secondary" disabled>
                Last <i class="fa fa-angle-double-right"></i>
            </button>
        {% endif %}
    </div>
</div>
```

### Option 2: Full Page Numbers
```html
<div class="pagination-wrapper" style="margin-top: 20px; text-align: center;">
    <ul class="pagination" style="display: inline-flex; gap: 5px; list-style: none; padding: 0;">
        {% if flood_records_page.has_previous %}
            <li><a href="?page=1" class="page-link">«</a></li>
            <li><a href="?page={{ flood_records_page.previous_page_number }}" class="page-link">‹</a></li>
        {% endif %}
        
        {% for num in paginator.page_range %}
            {% if flood_records_page.number == num %}
                <li><span class="page-link active" style="background: #2563eb; color: white;">{{ num }}</span></li>
            {% elif num > flood_records_page.number|add:'-3' and num < flood_records_page.number|add:'3' %}
                <li><a href="?page={{ num }}" class="page-link">{{ num }}</a></li>
            {% endif %}
        {% endfor %}
        
        {% if flood_records_page.has_next %}
            <li><a href="?page={{ flood_records_page.next_page_number }}" class="page-link">›</a></li>
            <li><a href="?page={{ paginator.num_pages }}" class="page-link">»</a></li>
        {% endif %}
    </ul>
    
    <div style="margin-top: 10px; color: #64748b; font-size: 14px;">
        Page {{ flood_records_page.number }} of {{ paginator.num_pages }} 
        ({{ paginator.count }} total records)
    </div>
</div>
```

### Option 3: Records Per Page Selector
Add this dropdown to let users choose how many records to show:

```html
<div style="margin-bottom: 15px;">
    <label for="perPageSelect" style="margin-right: 10px;">Records per page:</label>
    <select id="perPageSelect" class="form-select" style="width: auto; display: inline-block;" onchange="changePerPage(this.value)">
        <option value="10" {% if request.GET.per_page == '10' %}selected{% endif %}>10</option>
        <option value="20" {% if request.GET.per_page == '20' or not request.GET.per_page %}selected{% endif %}>20</option>
        <option value="50" {% if request.GET.per_page == '50' %}selected{% endif %}>50</option>
        <option value="100" {% if request.GET.per_page == '100' %}selected{% endif %}>100</option>
    </select>
</div>

<script>
function changePerPage(perPage) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', perPage);
    url.searchParams.set('page', '1');  // Reset to page 1
    window.location.href = url.toString();
}
</script>
```

## Preserving Other Query Parameters
If you have filters (e.g., `?time_range=7d`), preserve them:

```html
<a href="?page={{ flood_records_page.next_page_number }}&time_range={{ time_range }}" class="btn btn-primary">
    Next
</a>
```

Or use JavaScript:
```javascript
function navigateToPage(pageNum) {
    const url = new URL(window.location);
    url.searchParams.set('page', pageNum);
    window.location.href = url.toString();
}
```

## Testing URLs
- Default: `/monitoring/` - Shows page 1, 20 records
- Page 2: `/monitoring/?page=2`
- Custom size: `/monitoring/?per_page=50`
- Combined: `/monitoring/?page=2&per_page=50`

## Where to Add in Template
Look for the flood records table in `monitoring.html` and add the pagination controls:
1. **Above the table** - For quick navigation
2. **Below the table** - Standard position
3. **Both** - Best UX for long tables
