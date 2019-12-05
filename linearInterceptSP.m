function accumulatedSegLength=linearInterceptSP(grains,phaseName,method,nLines,showPlot)
% grains = grain2d
% phaseName= String with name of the phase
% method = 'radial', 'grid', 'random'
% nLines= Number of lines for linear intercept
% segLength = array with linear intercepts for single phase
colors=lines;
accumulatedSegLength=[];
gb=grains.boundary;

if showPlot
    plot(grains);
end

% Linear intercept  - common to all methods
xtd=[min(grains.x) max(grains.x) min(grains.y) max(grains.y)];
mean_x=mean([xtd(1),xtd(2)]);
mean_y=mean([xtd(3),xtd(4)]);

%Get start and end coordinates for different methods
switch method
    
    case 'radial'
        % 1- Lines at different angles with origin at the maps'center    
        half_length_line=sqrt((xtd(2)-xtd(1))^2 + (xtd(4)-xtd(3))^2)/2;
        ang=linspace(0,pi-pi/nLines,nLines);
        x1=mean_x-half_length_line*sin(ang);
        y1=mean_y-half_length_line*cos(ang);
        x2=mean_x+half_length_line*sin(ang);
        y2=mean_y+half_length_line*cos(ang);
    
    case 'grid'
        % Calc grid spacing
        dxMargin=0.05*(range([xtd(1), xtd(2)]));
        dyMargin=0.05*(range([xtd(3), xtd(4)]));

        dx= linspace(xtd(1)+dxMargin, xtd(2)-dxMargin, round(nLines/2))';
        dy= linspace(xtd(3)+dyMargin, xtd(4)-dyMargin, round(nLines/2))';
        %Horizontal lines
        x1=repmat(xtd(1),round(nLines/2),1);% first x will be repeat the 
        y1=dy; %first y will be the y steps
        x2=repmat(xtd(2),round(nLines/2),1); %second x will be the maximum in x
        y2=dy;%second y will be also the y steps (=y1)
        % + Vertical lines
        x1=[x1; dx];% first x will be x steps
        y1=[y1; repmat(xtd(3),round(nLines/2),1)]; %first y will be the minimum y
        x2=[x2; dx]; % second x will be x steps
        y2=[y2, repmat(xtd(4),round(nLines/2),1)];%second y will be maximum in y
    
    case 'random'
        %Random coordinates inside the data dimensions
        x_pos=randi(round([xtd(1) xtd(2)]),nLines,2);
        y_pos=randi(round([xtd(3) xtd(4)]),nLines,2);
        x1=x_pos(:,1);
        y1=y_pos(:,1);
        x2=x_pos(:,2);
        y2=y_pos(:,2); 
        
    case 'circle'
        error('Circle method not yet implemented')
        % gb.intersect is not implemented for curves
        
        %Minimum circle diameter should be bigger than the biggest grain
        min_factor=1.5;
        min_diameter=min_factor*max(grains.diameter);
        % Max diameter is the total length of smaller dimension
        max_diameter=min( [range(xtd(1:2)), range(xtd(3:4))])
        %Circle steps:
        radius_step=linspace(min_diameter/2,max_diameter/2,nLines)
        %TODO...
end


for jj=1:nLines
    %Get start and end coordinates of intercept line
    x_pos=[x1(jj),x2(jj)];
    y_pos=[y1(jj),y2(jj)];
    
    % Get all the grains that this line intersects
    [x_intersect,~,~] = intersect(gb,[x_pos(1),y_pos(1)], [x_pos(2), y_pos(2)]);
    grains_id_intersect=unique(gb(~isnan(x_intersect)).grainId);
    if showPlot
        %plot lines:
        hold on
        plot(x_pos,y_pos,'Color',[colors(2,:),0.6], 'LineWidth',4,'HandleVisibility','off')
    end
    grains_id_intersect=grains_id_intersect(grains_id_intersect~=0);
    ind=id2ind(grains,grains_id_intersect);
    grains_id_intersect=grains.id(ind(ind~=0));

    grains_intersect=grains('id',grains_id_intersect);
    grains_intersect=grains_intersect(phaseName);
    
    % Isolate each grain and get its gb intersects with the line
     for ii=1:length(grains_intersect)
        gb_singleGrain=grains_intersect(ii).boundary;
        [x_int_sg, y_int_sg,segLength] = intersect(gb_singleGrain,[x_pos(1),y_pos(1)], [x_pos(2), y_pos(2)]);
        if segLength~=0
            if showPlot
                % plot segments cut by the line:
                hold on
                plot(x_int_sg(~isnan(x_int_sg)), y_int_sg(~isnan(x_int_sg)),'Color',[colors(6,:),0.95], 'LineWidth',2,'HandleVisibility','off');
                hold on
                scatter(x_int_sg(~isnan(x_int_sg)), y_int_sg(~isnan(x_int_sg)),'.k','HandleVisibility','off')
                hold off
            end
            accumulatedSegLength=[accumulatedSegLength,segLength];
        else
            accumulatedSegLength=[accumulatedSegLength,nan];
        end
     end
    
end
