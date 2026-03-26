%% =========================
% META-HUBS / ROI SELECTION (MODULE-WISE, FLEXIBLE)
%% =========================

% modules : vecteur [1 x nROI]
% group   : vecteur groupe sujet
% dimer_roi, trimer_roi : [nSubjects x nROI]

unique_modules = unique(modules);
selected_rois = [];

% ===== CHOIX DU MODE =====
selection_mode = 'all';  
% 'all'           -> toutes les ROI
% 'low_threshold' -> seuil faible par module
% 'topk'          -> top k par module

low_percentile = 30;   % seuil faible si mode = 'low_threshold'
k_fixed = 3;           % nb de ROI par module si mode = 'topk'

for m = unique_modules
    
    roi_in_module = find(modules == m);
    values = mean(trimer_roi(:, roi_in_module), 1, 'omitnan');
    
    switch selection_mode
        
        case 'all'
            rois_module = roi_in_module;
            
        case 'low_threshold'
            thr = prctile(values, low_percentile);
            rois_module = roi_in_module(values >= thr);
            
            % sécurité
            if isempty(rois_module)
                [~, idx_max] = max(values);
                rois_module = roi_in_module(idx_max);
            end
            
        case 'topk'
            k = min(k_fixed, length(roi_in_module));
            [~, idx_sorted] = sort(values, 'descend');
            rois_module = roi_in_module(idx_sorted(1:k));
            
        otherwise
            error('selection_mode inconnu');
    end
    
    selected_rois = [selected_rois rois_module];
    
    fprintf('Module %d : %d ROI sélectionnées\n', m, length(rois_module));
end

selected_rois = unique(selected_rois, 'stable');

fprintf('ROI sélectionnées total : %d / %d\n', length(selected_rois), nROI);
disp('Indices ROI sélectionnées :')
disp(selected_rois)
disp('Noms ROI sélectionnées :')
disp(ROI_names(selected_rois))


%% =========================
% COMPUTE MEAN + SEM PAR GROUPE
%% =========================

dimer_mean  = zeros(3,nROI);
dimer_sem   = zeros(3,nROI);

trimer_mean = zeros(3,nROI);
trimer_sem  = zeros(3,nROI);

for g = 1:3
    
    idx = (group == g);
    
    dimer_mean(g,:)  = mean(dimer_roi(idx,:), 1, 'omitnan');
    trimer_mean(g,:) = mean(trimer_roi(idx,:), 1, 'omitnan');
    
    dimer_sem(g,:)  = std(dimer_roi(idx,:), 0, 1, 'omitnan') ./ sqrt(sum(idx));
    trimer_sem(g,:) = std(trimer_roi(idx,:), 0, 1, 'omitnan') ./ sqrt(sum(idx));
    
end


%% =========================
% SUBPLOT ORGANISATION
%% =========================

nSel = length(selected_rois);
ncols = ceil(sqrt(nSel));
nrows = ceil(nSel / ncols);

% couleurs : dimers = tons pleins, trimers = tons plus clairs
colors_dimer = [ ...
    0.00 0.60 0.30;
    0.80 0.80 0.20;
    0.85 0.33 0.10
];

colors_trimer = [ ...
    0.40 0.85 0.65;
    0.95 0.95 0.55;
    1.00 0.55 0.35
];


%% =========================
% FIGURE UNIQUE : DIMER + TRIMER DANS LE MEME SUBPLOT
%% =========================

figure('Name','Dimers + Trimers (Module-wise)','Color','k')

for i = 1:nSel
    
    r = selected_rois(i);
    subplot(nrows, ncols, i)
    hold on
    
    % positions barres
    x_dimer  = [1 2 3];
    x_trimer = [1.35 2.35 3.35];
    
    vals_d = dimer_mean(:,r);
    err_d  = dimer_sem(:,r);
    
    vals_t = trimer_mean(:,r);
    err_t  = trimer_sem(:,r);
    
    % DIMER
    for g = 1:3
        bar(x_dimer(g), vals_d(g), 0.28, ...
            'FaceColor', colors_dimer(g,:), ...
            'EdgeColor', 'none');
    end
    
    % TRIMER
    for g = 1:3
        bar(x_trimer(g), vals_t(g), 0.28, ...
            'FaceColor', colors_trimer(g,:), ...
            'EdgeColor', 'none');
    end
    
    % erreurs
    errorbar(x_dimer, vals_d, err_d, 'w', 'LineStyle', 'none', 'LineWidth', 1)
    errorbar(x_trimer, vals_t, err_t, 'w', 'LineStyle', 'none', 'LineWidth', 1)
    
    xticks([1.175 2.175 3.175])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(sprintf('%s (M%d)', ROI_names{r}, modules(r)), 'Interpreter', 'none')
    
    ylabel('Strength')
    grid on
    box off
    
    % adapte automatiquement la limite Y
    ymax = max([vals_d + err_d; vals_t + err_t], [], 'all');
    if isempty(ymax) || isnan(ymax) || ymax <= 0
        ymax = 0.1;
    end
    ylim([0 ymax * 1.25])
    
    % légende seulement sur le premier subplot
    if i == 1
        h1 = bar(nan, nan, 'FaceColor', colors_dimer(1,:), 'EdgeColor', 'none');
        h2 = bar(nan, nan, 'FaceColor', colors_trimer(1,:), 'EdgeColor', 'none');
        legend([h1 h2], {'Dimer','Trimer'}, 'Location', 'best')
    end
end

sgtitle(sprintf('Dimer + Trimer Strength par ROI (%s)', selection_mode))

fprintf('\n===== DONE =====\n')